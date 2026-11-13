"""Load synthetic scenarios and build the simulated NAS state and baseline memory.

A scenario JSON may name a base file with "extends"; dictionaries are merged recursively,
lists are replaced, and a null value deletes the key (used to remove files from a base).
"""
from __future__ import annotations

import copy
import hashlib
import json
import posixpath
from dataclasses import dataclass, field
from pathlib import Path

from .sim import SimFile, SimNAS, inside, norm

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if value is None:
            merged.pop(key, None)
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def make_blob(spec: dict) -> bytes:
    if "format" in spec:
        from . import formats  # noqa: PLC0415
        if spec["format"] == "pdf":
            return formats.pdf(spec["text"])
        if spec["format"] == "docx":
            return formats.docx(spec["text"])
        if spec["format"] == "tiff":
            return formats.tiff(spec["text"], mark=spec.get("mark", False))
        raise ValueError(f"unknown format {spec['format']}")
    if "literal" in spec:
        return spec["literal"].encode("utf-8")
    unit = (spec["text"] + "\n").encode("utf-8")
    return (unit * (spec["size"] // len(unit) + 1))[: spec["size"]]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Memory:
    """Baseline memory: built from the fixture (the declared truth) or loaded from persisted bundles.

    observations is the set of observation IDs that copy records may cite; None means "not tracked"
    (only the presence of a citation is then checked).
    """
    scope_root: str
    baseline_time: int
    assets: dict[str, dict] = field(default_factory=dict)
    versions: dict[str, dict] = field(default_factory=dict)
    sets: dict[str, dict] = field(default_factory=dict)
    copies: list[dict] = field(default_factory=list)
    locations: dict[str, dict] = field(default_factory=dict)
    domains: dict[str, dict] = field(default_factory=dict)
    statements: dict[str, str] = field(default_factory=dict)
    rehearsed: set[str] = field(default_factory=set)
    rehearsals: list[dict] = field(default_factory=list)
    claims: list[dict] = field(default_factory=list)
    incomplete_locations: set[str] = field(default_factory=set)
    observations: set[str] | None = None
    scope_id: str = "SCP-0001"


@dataclass
class Scenario:
    id: str
    title: str
    covers: list[str]
    raw: dict
    blobs: dict[str, bytes]
    before: dict[str, SimFile]
    after: dict[str, SimFile]
    memory: Memory | None
    request: dict
    expected: dict
    faults: list[dict]
    policies: list[dict]

    @property
    def blob_sha(self) -> dict[str, str]:
        return {name: sha(data) for name, data in self.blobs.items()}

    def build_nas(self, files: dict[str, SimFile] | None = None, faults: list[dict] | None = None) -> SimNAS:
        """The post-incident NAS. The memory folder and the recovery parent exist: the user names them."""
        files = {p: SimFile(f.data, f.mtime) for p, f in (self.after if files is None else files).items()}
        declined = {d["op"] for d in self.raw.get("declined_approvals", [])}
        nas = SimNAS(files, faults=self.faults if faults is None else faults, blobs=self.blobs,
                     approve=lambda op, args: op not in declined)
        for folder in (self.request.get("memory_root", "cerbero-memory"), self.request.get("recovery_parent", "recovered")):
            nas.dirs.add(norm(folder))
            nas._add_parents(norm(folder))
        return nas

    def location_root(self, location_id: str) -> str:
        return norm(self.raw["locations"][location_id]["root"])


def _files(spec: dict, blobs: dict[str, bytes]) -> dict[str, SimFile]:
    return {norm(path): SimFile(blobs[entry["blob"]], entry.get("mtime", 1000)) for path, entry in spec.items()}


def apply_incident(files: dict[str, SimFile], ops: list[dict], blobs: dict[str, bytes]) -> dict[str, SimFile]:
    after = {p: SimFile(f.data, f.mtime) for p, f in files.items()}
    for op in ops:
        path = norm(op["path"])
        if op["op"] == "delete":
            after.pop(path)
        elif op["op"] == "rename":
            after[norm(op["to"])] = after.pop(path)
        elif op["op"] == "replace":
            mtime = after[path].mtime if op.get("keep_mtime") else op.get("mtime", after[path].mtime + 500)
            after[path] = SimFile(blobs[op["blob"]], mtime)
        elif op["op"] == "add":
            after[path] = SimFile(blobs[op["blob"]], op.get("mtime", 2000))
        else:
            raise ValueError(f"unknown incident op {op['op']}")
    return after


def build_memory(raw: dict, before: dict[str, SimFile], blobs: dict[str, bytes]) -> Memory | None:
    spec = raw.get("baseline")
    if not spec:
        return None
    scope_root = norm(raw["locations"][raw["request"]["scope"]]["root"])
    memory = Memory(scope_root=scope_root, baseline_time=max(f.mtime for f in before.values()))
    memory.locations = {lid: {"root": norm(l["root"]), "memberships": dict(l.get("memberships", {})),
                              "unknown_kinds": list(l.get("unknown_kinds", []))}
                        for lid, l in raw["locations"].items()}
    memory.domains = copy.deepcopy(raw.get("domains", {}))
    memory.statements = dict(raw.get("statements", {}))
    for vid, v in spec["versions"].items():
        data = blobs[v["blob"]]
        memory.versions[vid] = {"asset": v["asset"], "sha256": sha(data), "size": len(data)}
    for aid, a in spec["assets"].items():
        path = norm(a["path"])
        memory.assets[aid] = {"path": path, "importance": a["importance"], "current": a["current"],
                              "mtime": before[path].mtime if path in before else None,
                              "rel": posixpath.relpath(path, scope_root), "name": posixpath.basename(path)}
    memory.sets = copy.deepcopy(spec.get("sets", {}))
    by_sha: dict[str, list[str]] = {}
    for vid, v in memory.versions.items():
        by_sha.setdefault(v["sha256"], []).append(vid)
    seq = 0
    memory.observations = set()
    for lid, loc in memory.locations.items():
        for path in sorted(before):
            if not inside(path, loc["root"]):
                continue
            digest = sha(before[path].data)
            for vid in by_sha.get(digest, []):
                seq += 1
                memory.copies.append({"id": f"CPY-{seq:04d}", "version": vid, "path": path, "location": lid,
                                      "sha256": digest, "observation": f"OBS-0000-{seq:04d}", "access": "readable",
                                      "status": "current"})
                memory.observations.add(f"OBS-0000-{seq:04d}")
    for cid in spec.get("rehearsed_copies", []):
        memory.rehearsed.add(cid)
    memory.incomplete_locations = set(spec.get("inventory_incomplete", []))
    for claim in spec.get("claims", []):
        versions = set(memory.sets[claim["set"]]["members"].values()) if "set" in claim else set()
        depends = [c["id"] for c in memory.copies if c["version"] in versions] + claim.get("depends_on", [])
        memory.claims.append({"id": claim["id"], "statement": claim["statement"], "depends_on": depends,
                              "status": "current"})
    return memory


def load(path: Path | str) -> Scenario:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "extends" in raw:
        base = json.loads((FIXTURES / "bases" / raw["extends"]).read_text(encoding="utf-8"))
        raw = deep_merge(base, {k: v for k, v in raw.items() if k != "extends"})
    blobs = {name: make_blob(spec) for name, spec in raw["blobs"].items()}
    before = _files(raw["before"], blobs)
    after = apply_incident(before, raw.get("incident", []), blobs)
    return Scenario(
        id=raw["id"], title=raw["title"], covers=raw.get("covers", []), raw=raw, blobs=blobs,
        before=before, after=after, memory=build_memory(raw, before, blobs),
        request=raw["request"], expected=raw.get("expected", {}), faults=raw.get("faults", []),
        policies=raw.get("active_policies", []),
    )


def load_all(kind: str = "scenarios") -> list[Scenario]:
    return [load(p) for p in sorted((FIXTURES / kind).glob("*.json"))]
