"""Simulated NAS experts for development evaluation.

The simulator models the semantics Cerbero assumes from catalog 2.0.0 (stat, ls, find with
an exact size filter, sha256sum, cat, mkdir, cpmv copy without overwrite, document qa,
save-text). Catalog permissions, prerequisites and error codes are published as unknown,
so every behaviour here is an assumption that still has to be validated on UGOS.
"""
from __future__ import annotations

import hashlib
import posixpath
from collections import Counter
from dataclasses import dataclass

DEFAULT_LIST_LIMIT = 200
STATE_CHANGE_OPS = {"mkdir", "copy", "save_text", "delete", "move"}


def norm(path: str) -> str:
    return posixpath.normpath(path.strip("/"))


def inside(path: str, root: str) -> bool:
    path, root = norm(path), norm(root)
    return path == root or path.startswith(root + "/")


@dataclass
class SimFile:
    data: bytes
    mtime: int


def ok(**data):
    return {"ok": True, "data": data}


def err(code: str, **data):
    return {"ok": False, "error": {"code": code, **data}}


class SimNAS:
    """In-memory file tree with fault injection and operation accounting."""

    def __init__(self, files: dict[str, SimFile], faults: list[dict] | None = None,
                 approve=None, blobs: dict[str, bytes] | None = None, clock: int = 10_000):
        self.files = {norm(p): f for p, f in files.items()}
        self.dirs: set[str] = set()
        for path in self.files:
            self._add_parents(path)
        self.faults = [dict(f) for f in (faults or [])]
        self.approve = approve or (lambda op, args: True)
        self.blobs = blobs or {}
        self.clock = clock
        self.calls: Counter = Counter()
        self.bytes_hashed = 0
        self.approvals_requested = 0
        self.approvals_declined = 0
        self.overwrite_attempts = 0
        self.log: list[tuple[str, dict, bool]] = []

    # -- helpers ---------------------------------------------------------
    def _add_parents(self, path: str) -> None:
        parent = posixpath.dirname(path)
        while parent and parent not in self.dirs:
            self.dirs.add(parent)
            parent = posixpath.dirname(parent)

    def _denied(self, path: str) -> bool:
        return any(f["kind"] == "permission_denied" and inside(path, f["prefix"]) for f in self.faults)

    def _limit(self, requested: int | None) -> int:
        limits = [f["limit"] for f in self.faults if f["kind"] == "list_limit"]
        candidates = [requested or DEFAULT_LIST_LIMIT] + limits
        return min(candidates)

    def _record(self, op: str, args: dict, result: dict) -> dict:
        self.calls[op] += 1
        self.log.append((op, args, result["ok"]))
        return result

    def _resolve(self, path: str) -> str:
        """Follow link faults: a link at a path (or a folder prefix) resolves to its target."""
        for fault in self.faults:
            if fault["kind"] == "link" and inside(path, fault["path"]):
                link = norm(fault["path"])
                return norm(norm(fault["target"]) + path[len(link):])
        return path

    def _omits_realpath(self, op: str, path: str) -> bool:
        return any(f["kind"] == "omit_realpath" and f["op"] == op and inside(path, f.get("prefix", ""))
                   and posixpath.basename(path).startswith(f.get("name_prefix", "")) for f in self.faults)

    def _save_fault(self, hint: str, content: str) -> str | None:
        """A fault applies to saves whose name hint starts with hint_prefix and, if given, whose text holds a
        record of record_type (so a fault can target the plan or the receipt whatever its bundle number)."""
        for fault in self.faults:
            if fault["kind"] in ("save_fail", "save_unverified", "save_incomplete", "save_elsewhere", "save_partial") \
                    and hint.startswith(fault.get("hint_prefix", "")) \
                    and ("record_type" not in fault or f'- type: "{fault["record_type"]}"' in content):
                return fault["kind"]
        return None

    def _size_limit(self) -> int | None:
        limits = [f["bytes"] for f in self.faults if f["kind"] == "save_size_limit"]
        return min(limits) if limits else None

    def _approval(self, op: str, args: dict) -> bool:
        self.approvals_requested += 1
        granted = bool(self.approve(op, args))
        if not granted:
            self.approvals_declined += 1
        return granted

    def exists(self, path: str) -> bool:
        path = norm(path)
        return path in self.files or path in self.dirs

    def content(self, path: str) -> bytes | None:
        entry = self.files.get(norm(path))
        return entry.data if entry else None

    # -- read operations ---------------------------------------------------
    def stat(self, path: str) -> dict:
        path = norm(path)
        args = {"path": path}
        real = self._resolve(path)
        if self._denied(path) or self._denied(real):
            return self._record("stat", args, err("permission_denied", path=path))
        extra = {} if self._omits_realpath("stat", path) else {"realpath": real}
        if real in self.files:
            f = self.files[real]
            return self._record("stat", args, ok(path=path, **extra, type="file", size=len(f.data), mtime=f.mtime))
        if real in self.dirs:
            return self._record("stat", args, ok(path=path, **extra, type="dir"))
        return self._record("stat", args, err("not_found", path=path))

    def _walk(self, root: str, max_depth: int | None):
        """Yield readable files under root and collect unreadable subfolders."""
        denied: set[str] = set()
        found = []
        base_depth = root.count("/") + 1 if root else 0
        for path in sorted(self.files):
            if not inside(path, root) or path == root:
                continue
            if max_depth is not None and path.count("/") + 1 - base_depth > max_depth:
                continue
            blocked = [f["prefix"] for f in self.faults if f["kind"] == "permission_denied" and inside(path, f["prefix"])]
            if blocked:
                denied.update(norm(b) for b in blocked)
                continue
            found.append(path)
        return found, sorted(denied)

    def find(self, root: str, size: int | None = None, limit: int | None = None,
             max_depth: int | None = None, newer_than: int | None = None,
             suffixes: tuple[str, ...] | None = None) -> dict:
        root = norm(root)
        args = {"path": root, "size": size, "limit": limit, "max_depth": max_depth}
        if self._denied(root):
            return self._record("find", args, err("permission_denied", path=root))
        if root not in self.dirs:
            return self._record("find", args, err("not_found", path=root))
        paths, denied = self._walk(root, max_depth)
        entries = []
        for path in paths:
            f = self.files[path]
            if size is not None and len(f.data) != size:
                continue
            if newer_than is not None and f.mtime <= newer_than:
                continue
            if suffixes and not path.lower().endswith(suffixes):
                continue
            entries.append({"path": path, "realpath": self._resolve(path), "size": len(f.data), "mtime": f.mtime})
        cap = self._limit(limit)
        return self._record("find", args, ok(entries=entries[:cap], truncated=len(entries) > cap, denied=denied))

    def ls(self, root: str, limit: int | None = None, name_contains: str | None = None) -> dict:
        """Direct children of root, each with its real path; name_contains models a name pattern filter."""
        root = norm(root)
        args = {"path": root, "limit": limit, "name_contains": name_contains}
        if self._denied(root):
            return self._record("ls", args, err("permission_denied", path=root))
        if root not in self.dirs:
            return self._record("ls", args, err("not_found", path=root))
        children = set()
        for path in list(self.files) + list(self.dirs):
            if posixpath.dirname(path) == root and (name_contains is None or name_contains in posixpath.basename(path)):
                children.add(path)
        entries = []
        for p in sorted(children):
            entry = {"path": p, "type": "dir" if p in self.dirs else "file"}
            if not self._omits_realpath("ls", p):
                entry["realpath"] = self._resolve(p)
            entries.append(entry)
        cap = self._limit(limit)
        return self._record("ls", args, ok(entries=entries[:cap], truncated=len(entries) > cap))

    def sha256(self, path: str) -> dict:
        path = norm(path)
        args = {"path": path}
        real = self._resolve(path)
        if self._denied(path) or self._denied(real):
            return self._record("sha256", args, err("permission_denied", path=path))
        if real not in self.files:
            return self._record("sha256", args, err("not_found", path=path))
        data = self.files[real].data
        self.bytes_hashed += len(data)
        extra = {} if self._omits_realpath("sha256", path) else {"realpath": real}
        return self._record("sha256", args, ok(path=path, **extra, sha256=hashlib.sha256(data).hexdigest(),
                                               size=len(data)))

    def cat(self, path: str) -> dict:
        path = norm(path)
        args = {"path": path}
        real = self._resolve(path)
        if self._denied(path) or self._denied(real):
            return self._record("cat", args, err("permission_denied", path=path))
        if real not in self.files:
            return self._record("cat", args, err("not_found", path=path))
        data = self.files[real].data
        cut = next((f["bytes"] for f in self.faults if f["kind"] == "truncate_read" and inside(path, f["prefix"])), None)
        if cut is not None and cut < len(data):
            return self._record("cat", args, ok(path=path, realpath=real, partial=True, bytes_returned=cut,
                                                text=data[:cut].decode("utf-8", "replace")))
        return self._record("cat", args, ok(path=path, realpath=real, text=data.decode("utf-8", "replace")))

    def doc_qa(self, path: str, question: str) -> dict:
        """document-agent stand-in: returns the document text as quoted passages, no reasoning."""
        path = norm(path)
        args = {"path": path, "question": question}
        if self._denied(path) or path not in self.files:
            return self._record("doc_qa", args, err("not_readable", path=path))
        text = self.files[path].data.decode("utf-8", "replace")
        passages = [line.strip() for line in text.splitlines() if line.strip()]
        return self._record("doc_qa", args, ok(path=path, quotes=passages, coverage="full"))

    def open_check(self, path: str) -> dict:
        """document-agent stand-in for reading a whole document: PDF and DOCX only, as a format check."""
        from . import formats  # noqa: PLC0415
        path = norm(path)
        args = {"path": path}
        real = self._resolve(path)
        if self._denied(path) or real not in self.files:
            return self._record("open_check", args, err("not_readable", path=path))
        data = self.files[real].data
        suffix = posixpath.splitext(path)[1].lower()
        if suffix not in (".pdf", ".docx"):
            return self._record("open_check", args, err("not_supported", path=path))
        try:
            opened = formats.check_pdf(data) if suffix == ".pdf" else bool(formats.docx_text(data) is not None)
        except Exception:  # noqa: BLE001 - any parse error means the document did not open
            opened = False
        if not opened:
            return self._record("open_check", args, err("not_readable", path=path))
        return self._record("open_check", args, ok(path=path, realpath=real, read="whole file", format=suffix[1:]))

    # -- state-changing operations ----------------------------------------------
    def mkdir(self, path: str) -> dict:
        path = norm(path)
        args = {"path": path}
        if self.exists(path):
            return self._record("mkdir", args, err("exists", path=path))
        if not self._approval("mkdir", args):
            return self._record("mkdir", args, err("approval_declined"))
        self.dirs.add(path)
        self._add_parents(path)
        return self._record("mkdir", args, ok(path=path, realpath=self._resolve(path)))

    def copy(self, src: str, dst: str) -> dict:
        src, dst = norm(src), norm(dst)
        args = {"src": src, "dst": dst}
        real_src = self._resolve(src)
        if self._denied(src) or self._denied(real_src) or real_src not in self.files:
            return self._record("copy", args, err("source_unavailable", path=src))
        src = real_src
        if self.exists(dst):
            self.overwrite_attempts += 1
            return self._record("copy", args, err("exists", path=dst))
        if posixpath.dirname(dst) not in self.dirs:
            return self._record("copy", args, err("parent_missing", path=dst))
        if not self._approval("copy", args):
            return self._record("copy", args, err("approval_declined"))
        for fault in self.faults:
            if fault["kind"] == "copy_fail" and norm(fault["src"]) == src and fault.get("times", 1) > 0:
                fault["times"] = fault.get("times", 1) - 1
                return self._record("copy", args, err("copy_failed", path=src))
        for fault in self.faults:
            if fault["kind"] == "mutate_on_copy" and norm(fault["src"]) == src and not fault.get("done"):
                fault["done"] = True
                self.files[src] = SimFile(self.blobs[fault["blob"]], self.files[src].mtime)
        self.clock += 1
        self.files[dst] = SimFile(self.files[src].data, self.clock)
        self._add_parents(dst)
        return self._record("copy", args, ok(src=src, dst=dst, realpath=dst))

    def save_text(self, folder: str, hint: str, content: str) -> dict:
        """save-text stand-in. The folder must exist; faults model refusals and incomplete answers."""
        folder = norm(folder)
        path = norm(f"{folder}/{hint}.md")
        args = {"folder": folder, "hint": hint}
        if folder not in self.dirs:
            return self._record("save_text", args, err("not_found", path=folder))
        if path in self.files:
            return self._record("save_text", args, err("exists", path=path))
        if not self._approval("save_text", args):
            return self._record("save_text", args, err("approval_declined"))
        fault = self._save_fault(hint, content)
        if fault == "save_fail":
            return self._record("save_text", args, err("save_failed", path=path))
        data = content.encode("utf-8")
        limit = self._size_limit()
        if limit is not None and len(data) > limit:
            return self._record("save_text", args, err("too_large", path=path, limit=limit))
        if fault == "save_elsewhere":
            path = norm(f"elsewhere/{hint}.md")
        if fault == "save_partial":
            data = data[: len(data) // 2]
        self.clock += 1
        self.files[path] = SimFile(data, self.clock)
        self._add_parents(path)
        if fault == "save_incomplete":
            return self._record("save_text", args, ok(verified=True, contentBytes=len(data)))
        return self._record("save_text", args, ok(outputFile=path, verified=fault != "save_unverified",
                                                   contentBytes=len(data)))

    def delete(self, path: str) -> dict:
        """Exposed only so tests can prove Cerbero never calls it."""
        path = norm(path)
        args = {"path": path}
        if not self._approval("delete", args):
            return self._record("delete", args, err("approval_declined"))
        self.files.pop(path, None)
        return self._record("delete", args, ok(path=path))

    # -- accounting ----------------------------------------------------------
    def state_changes(self) -> int:
        return sum(1 for op, _, success in self.log if op in STATE_CHANGE_OPS and success)

    def stats(self) -> dict:
        return {
            "calls_total": sum(self.calls.values()),
            "calls_read": sum(n for op, n in self.calls.items() if op not in STATE_CHANGE_OPS),
            "state_changes": self.state_changes(),
            "approvals_requested": self.approvals_requested,
            "approvals_declined": self.approvals_declined,
            "bytes_hashed": self.bytes_hashed,
            "digests": self.calls["sha256"],
            "saves": self.calls["save_text"],
            "overwrite_attempts": self.overwrite_attempts,
            "forbidden_calls": self.calls["delete"] + self.calls["move"],
        }
