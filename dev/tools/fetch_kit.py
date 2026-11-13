"""Download the official Uliya Skill Kit 0.7.3 into dev/.kit and verify its SHA-256.

The kit is used only to run the official static checker during development.
It is not redistributed and is never copied into the Skill package.
"""
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

KIT_URL = "https://cdn.shopify.com/s/files/1/0630/9416/1602/files/uliya-skill-kit-0.7.3-en.zip?v=1790578898"
KIT_SHA256 = "cf557e5a022e4297892f39768132855154232efdedeb726b2845450ccd70e1b3"
KIT_DIR = Path(__file__).resolve().parents[1] / ".kit"


def main() -> int:
    KIT_DIR.mkdir(parents=True, exist_ok=True)
    archive = KIT_DIR / "uliya-skill-kit-0.7.3-en.zip"
    if not archive.exists():
        with urllib.request.urlopen(KIT_URL, timeout=60) as response:
            archive.write_bytes(response.read())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != KIT_SHA256:
        print(f"kit digest mismatch: {digest}", file=sys.stderr)
        return 1
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.namelist():
            target = (KIT_DIR / member).resolve()
            if KIT_DIR.resolve() not in target.parents and target != KIT_DIR.resolve():
                print(f"unsafe member path: {member}", file=sys.stderr)
                return 1
        bundle.extractall(KIT_DIR)
    print(f"kit ready at {KIT_DIR / 'uliya-skill-kit'} (sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
