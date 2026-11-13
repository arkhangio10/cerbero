"""Run the official Uliya static checker (kit 0.7.3) against a Skill directory.

Usage: python tools/check_skill.py [skill-dir]   (default: skill/cerbero-guardian)
Requires Node.js and the kit fetched with tools/fetch_kit.py. A static pass does not prove
upload, installation, compatibility or device execution.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "dev" / ".kit" / "uliya-skill-kit"
DEFAULT_SKILL = ROOT / "skill" / "cerbero-guardian"


def run_checker(skill_dir: Path) -> dict:
    script = KIT / "scripts" / "check-skill.mjs"
    if not script.exists():
        raise FileNotFoundError("kit not found: run python dev/tools/fetch_kit.py")
    completed = subprocess.run(["node", str(script), str(skill_dir)], capture_output=True, text=True,
                               encoding="utf-8", check=False)
    if completed.returncode == 2:
        raise RuntimeError(completed.stderr.strip())
    return json.loads(completed.stdout)


def main(argv: list[str]) -> int:
    skill_dir = Path(argv[1]) if len(argv) > 1 else DEFAULT_SKILL
    result = run_checker(skill_dir.resolve())
    print(f"status: {result['status']}  errors: {result['summary']['errors']}  "
          f"warnings: {result['summary']['warnings']}  files: {len(result['files'])}")
    for item in result["diagnostics"]:
        print(f"  {item['severity']} {item['code']} {item.get('file', '')}:{item.get('line', '')} {item['message']}")
    return 0 if result["status"] != "not-uploadable" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
