"""Path scope rules of references/trust-and-boundaries.md ("Paths and scope"), as deterministic code.

A path is accepted only in canonical form: no empty, "." or ".." component, no backslash, no control
character, and the same absolute/relative kind as its root. Containment is decided component by
component on the exact strings; a match that only appears after Unicode normalization or case folding
is reported as an alias and rejected. Real paths returned by an expert are checked the same way; a
result without a real path cannot prove containment, so the dependent operation is blocked.
"""
from __future__ import annotations

import unicodedata

SCOPE_FAILURES = {"outside", "non-canonical path", "non-canonical root", "unexpected absolute path",
                  "relative path for an absolute root", "unicode-alias", "case-alias", "real path not reported"}


def canonical(path) -> bool:
    if not isinstance(path, str) or path in ("", "/"):
        return False
    if "\\" in path or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in path):
        return False
    body = path[1:] if path.startswith("/") else path
    return all(part not in ("", ".", "..") for part in body.split("/"))


def _parts(path: str) -> list[str]:
    return (path[1:] if path.startswith("/") else path).split("/")


def containment(path, root) -> str:
    """inside, outside, or the reason the question cannot be answered safely."""
    if not canonical(root):
        return "non-canonical root"
    if not canonical(path):
        return "non-canonical path"
    if path.startswith("/") != root.startswith("/"):
        return "unexpected absolute path" if path.startswith("/") else "relative path for an absolute root"
    p, r = _parts(path), _parts(root)
    head = p[:len(r)]
    if head == r:
        return "inside"
    if len(head) == len(r):
        if [unicodedata.normalize("NFC", x) for x in head] == [unicodedata.normalize("NFC", x) for x in r]:
            return "unicode-alias"
        if [x.casefold() for x in head] == [x.casefold() for x in r]:
            return "case-alias"
    return "outside"


def inside(path, root) -> bool:
    return containment(path, root) == "inside"


def relative_inside(path, root) -> tuple[str | None, str]:
    """The path of a file relative to a root it lies strictly inside, or None with the reason."""
    verdict = containment(path, root)
    if verdict != "inside":
        return None, verdict
    rest = _parts(path)[len(_parts(root)):]
    return ("/".join(rest), "inside") if rest else (None, "the root itself")


def child(root, rel) -> tuple[str | None, str]:
    """root/rel when rel is a canonical relative path that stays strictly inside root."""
    if not isinstance(rel, str) or rel.startswith("/"):
        return None, "unexpected absolute path"
    if not canonical(rel):
        return None, "non-canonical path"
    path = f"{root}/{rel}"
    verdict = containment(path, root)
    return (path, "inside") if verdict == "inside" else (None, verdict)


def real_inside(result: dict, root) -> tuple[bool, str]:
    """Whether an expert result proves that the real path it reports lies inside root."""
    if not result.get("ok"):
        return False, "no result"
    real = result["data"].get("realpath")
    if real is None:
        return False, "real path not reported"
    verdict = containment(real, root)
    return verdict == "inside", verdict
