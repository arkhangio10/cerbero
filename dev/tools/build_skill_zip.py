"""Build a versioned Skill ZIP, verify the official limits and re-check the extracted copy.

Usage: python tools/build_skill_zip.py [version]   (default 1.0.0)
Writes dist/cerbero-guardian-<version>.zip and refuses to overwrite an existing version.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

from check_skill import ROOT, run_checker

SKILL = ROOT / "skill" / "cerbero-guardian"
DIST = ROOT / "dist"
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_ZIP_BYTES = 100, 1024 * 1024, 10 * 1024 * 1024, 10 * 1024 * 1024


def package_files() -> list[Path]:
    files = sorted(p for p in SKILL.rglob("*") if p.is_file())
    unexpected = [p for p in files if p.suffix != ".md" or not (p.name == "SKILL.md" or p.parent.name == "references")]
    if unexpected:
        raise ValueError(f"unsupported files in package: {unexpected}")
    return files


def build(version: str) -> Path:
    files = package_files()
    sizes = [p.stat().st_size for p in files]
    if len(files) > MAX_FILES or max(sizes) > MAX_FILE_BYTES or sum(sizes) > MAX_TOTAL_BYTES:
        raise ValueError("package exceeds official limits")
    DIST.mkdir(exist_ok=True)
    target = DIST / f"cerbero-guardian-{version}.zip"
    if target.exists():
        raise FileExistsError(f"{target.name} already exists; choose a new version")
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(f"cerbero-guardian/{path.relative_to(SKILL).as_posix()}", date_time=(2026, 11, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, path.read_bytes())
    if target.stat().st_size > MAX_ZIP_BYTES:
        target.unlink()
        raise ValueError("ZIP exceeds 10 MB")
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(target) as bundle:
        bundle.extractall(tmp)
        result = run_checker(Path(tmp) / "cerbero-guardian")
    if result["status"] != "static-pass":
        target.unlink()
        raise RuntimeError(f"extracted package did not pass: {result['summary']}")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"{target.relative_to(ROOT)}  files={len(files)}  unpacked={sum(sizes)} B  zip={target.stat().st_size} B  "
          f"checker={result['status']}  sha256={digest}")
    return target


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "1.0.0")
