"""Development harness: a model follows the real SKILL.md while simulated experts answer its delegations.

Usage (normally through the nas.sh wrapper written by runner.py):
  harness.py --session DIR delegate --target AGENT --instruction TEXT
  harness.py --session DIR resume --approval ID
  harness.py --session DIR ask-user --question TEXT     (waiting_user: a question that waits for the reply)
  harness.py --session DIR tell --message TEXT          (a notice to the user that does not wait)
  harness.py --session DIR finish --report-file PATH

Experts accept only instructions that match one of the delegate templates written in SKILL.md, with
slots filled as the slot table says (list slots are JSON arrays). State changes answer waiting_approval
first; the simulated user decides when the agent calls resume. Every command and answer is appended to
DIR/trace.jsonl. Paths shown to the agent carry the prefix /data/studio, like the absolute real paths of a NAS.
This is a local agent evaluation with simulated experts. It is not UGOS and not a device test.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path

DEV = Path(__file__).resolve().parents[1]
ROOT = DEV.parent
sys.path.insert(0, str(DEV))

from cerbero_lab import scope  # noqa: E402
from cerbero_lab.sim import SimFile, SimNAS  # noqa: E402

PREFIX = "/data/studio"
SKILL = ROOT / "skill" / "cerbero-guardian" / "SKILL.md"
LIST_SLOTS = {"folder_list", "path_list", "file_list", "subfolder_list"}
STATE_CHANGES = {"D10", "D11", "D12"}
_DELEGATE = re.compile(r"^(D\d+) `delegate --target (\S+) --instruction '([^']*)'`$", re.M)
_SLOT = re.compile(r"\{([a-z_]+)\}")
_SIZE = re.compile(r"^whose size is exactly (\d+) bytes$")


def templates() -> dict[str, tuple[str, re.Pattern, list[str]]]:
    """D-number -> (target, compiled pattern, slot names) from the delegate commands in SKILL.md."""
    found = {}
    for number, target, text in _DELEGATE.findall(SKILL.read_text(encoding="utf-8")):
        parts, slots, last = [], [], 0
        for match in _SLOT.finditer(text):
            literal = text[last:match.start()]
            parts.append(r"\s+".join(re.escape(w) for w in literal.split(" ")) if literal.strip() else re.escape(literal))
            slots.append(match.group(1))
            parts.append(r"(.*)" if match.end() == len(text) else r"(.+?)")
            last = match.end()
        tail = text[last:]
        parts.append(r"\s+".join(re.escape(w) for w in tail.split(" ")) if tail.strip() else re.escape(tail))
        found[number] = (target, re.compile(r"\s*" + "".join(parts) + r"\s*", re.S), slots)
    return found


def to_sim(path: str) -> str | None:
    """Agent path -> simulator path, or None when the path is not under the NAS volume shown to the agent."""
    if not isinstance(path, str) or not path.startswith(PREFIX + "/"):
        return None
    return path[len(PREFIX) + 1:]


def to_agent(path: str | None) -> str | None:
    return None if path is None else f"{PREFIX}/{path}"


class Session:
    def __init__(self, directory: Path):
        self.dir = directory
        self.state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        s = self.state
        self.nas = SimNAS({p: SimFile(base64.b64decode(f["data"]), f["mtime"]) for p, f in s["files"].items()},
                          faults=s["faults"], approve=self._approve)
        self.nas.dirs = set(s["dirs"])
        self.nas.clock = s["clock"]
        self.nas.calls.update(s["calls"])
        self.nas.log = [tuple(x) for x in s["log"]]
        self.decision = True

    def _approve(self, op, args) -> bool:
        return self.decision

    def save(self):
        s = self.state
        s["files"] = {p: {"data": base64.b64encode(f.data).decode(), "mtime": f.mtime} for p, f in self.nas.files.items()}
        s["dirs"] = sorted(self.nas.dirs)
        s["clock"] = self.nas.clock
        s["calls"] = dict(self.nas.calls)
        s["log"] = [list(x) for x in self.nas.log]
        s["faults"] = self.nas.faults
        (self.dir / "state.json").write_text(json.dumps(s), encoding="utf-8")

    def trace(self, entry: dict):
        self.state["seq"] += 1
        entry = {"seq": self.state["seq"], **entry}
        with (self.dir / "trace.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def parse_slots(number: str, values: dict[str, str]) -> tuple[dict | None, str | None]:
    out = {}
    for name, raw in values.items():
        if name in LIST_SLOTS:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return None, f"{name} is not a JSON array"
            if not isinstance(parsed, list) or not all(isinstance(v, str) for v in parsed):
                return None, f"{name} is not a JSON array of strings"
            out[name] = parsed
        elif name == "expected_digests":
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return None, "expected_digests is not a JSON object"
            if not isinstance(parsed, dict):
                return None, "expected_digests is not a JSON object"
            out[name] = parsed
        elif name in ("limit", "max_depth", "hash_budget"):
            if not raw.strip().isdigit():
                return None, f"{name} is not a number"
            out[name] = int(raw)
        else:
            out[name] = raw
    return out, None


def stat_row(nas, path):
    if path == PREFIX:
        return {"path": path, "exists": True, "type": "dir", "readable": True, "real_path": PREFIX}
    sim = to_sim(path)
    if sim is None:
        return {"path": path, "exists": False, "reason": "not found"}
    result = nas.stat(sim)
    if not result["ok"]:
        return {"path": path, "exists": False, "reason": result["error"]["code"]}
    data = result["data"]
    row = {"path": path, "exists": True, "type": data["type"], "readable": True}
    if "realpath" in data:
        row["real_path"] = to_agent(data["realpath"])
    if data["type"] == "file":
        row.update(size_bytes=data["size"], modified=data["mtime"])
    return row


def run_read(session: Session, number: str, slots: dict) -> dict:
    nas = session.nas
    if number == "D1":
        return {"real_path": PREFIX}
    if number == "D2":
        return {"folders": [stat_row(nas, p) for p in slots["folder_list"]]}
    if number in ("D3", "D13"):
        root = slots["memory_root" if number == "D3" else "search_root"]
        sim = to_sim(root)
        pattern = slots.get("name_filter") if number == "D3" else None
        listing = nas.ls(sim, limit=slots["limit"], name_contains=pattern) if sim is not None \
            else {"ok": False, "error": {"code": "not_found"}}
        if not listing["ok"]:
            return {"failed": listing["error"]["code"]}
        kind = "file" if number == "D3" else "dir"
        entries = [e for e in listing["data"]["entries"] if e["type"] == kind]
        if number == "D3":
            rows = []
            for e in entries:
                st = nas.stat(e["path"])
                row = {"name": Path(e["path"]).name, "size_bytes": st["data"].get("size") if st["ok"] else None,
                       "modified": st["data"].get("mtime") if st["ok"] else None}
                if e.get("realpath"):
                    row["real_path"] = to_agent(e["realpath"])
                rows.append(row)
            return {"files": rows, "truncated": listing["data"]["truncated"], "empty": not rows}
        return {"subfolders": [{"real_path": to_agent(e["path"])} for e in entries],
                "truncated": listing["data"]["truncated"], "unreadable": [], "empty": not entries}
    if number == "D4":
        out = []
        for path in slots["file_list"]:
            sim = to_sim(path)
            result = nas.cat(sim) if sim is not None else {"ok": False, "error": {"code": "not_found"}}
            out.append({"path": path, "text": result["data"]["text"]} if result["ok"]
                       else {"path": path, "missing_or_unreadable": result["error"]["code"]})
        return {"files": out}
    if number == "D5":
        return {"paths": [stat_row(nas, p) for p in slots["path_list"]]}
    if number == "D6":
        sim = to_sim(slots["search_root"])
        size = None
        if slots["size_filter"].strip() != "of any size":
            match = _SIZE.match(slots["size_filter"].strip())
            if not match:
                return {"failed": "size filter not understood"}
            size = int(match.group(1))
        result = nas.find(sim, size=size, limit=slots["limit"], max_depth=slots["max_depth"]) if sim is not None \
            else {"ok": False, "error": {"code": "not_found"}}
        if not result["ok"]:
            return {"failed": result["error"]["code"]}
        data = result["data"]
        return {"files": [{"real_path": to_agent(e["realpath"]), "size_bytes": e["size"], "modified": e["mtime"]}
                          for e in data["entries"]],
                "truncated": data["truncated"], "unreadable_subfolders": [to_agent(d) for d in data["denied"]],
                "empty": not data["entries"]}
    if number == "D7":
        rows = []
        for n, path in enumerate(slots["path_list"]):
            if n >= slots["hash_budget"]:
                rows.append({"path": path, "not_processed": "hash budget reached"})
                continue
            sim = to_sim(path)
            result = nas.sha256(sim) if sim is not None else {"ok": False, "error": {"code": "not_found"}}
            if not result["ok"]:
                rows.append({"path": path, "missing_or_unreadable": result["error"]["code"]})
                continue
            row = {"path": path, "sha256": result["data"]["sha256"], "size_bytes": result["data"]["size"]}
            if "realpath" in result["data"]:
                row["real_path"] = to_agent(result["data"]["realpath"])
            if path in slots["expected_digests"]:
                row["matches_expected"] = slots["expected_digests"][path] == row["sha256"]
            rows.append(row)
        return {"digests": rows}
    if number == "D8":
        sim = to_sim(slots["document_path"])
        quotes = document_text(nas, sim) if sim is not None else None
        if quotes is None:
            return {"failed": "the file cannot be read as a document"}
        return {"answer": "The answer can only come from the quoted passages; the file contains no other text.",
                "quotes": quotes, "read": "the whole file"}
    if number == "D9":
        return {"answer": "No official answer exists for this question.", "references": []}
    raise ValueError(number)


def document_text(nas, sim: str) -> list[str] | None:
    """document-agent stand-in: text lines of a plain-text note, a valid PDF or a valid DOCX; None otherwise."""
    from cerbero_lab import formats  # noqa: PLC0415
    seen = nas.doc_qa(sim, "read")
    if not seen["ok"]:
        return None
    data = nas.content(sim)
    try:
        if sim.lower().endswith(".pdf"):
            if not formats.check_pdf(data):
                return None
            return [m.decode("latin-1") for m in re.findall(rb"\((.*?)\) Tj", data)]
        if sim.lower().endswith(".docx"):
            return [line for line in formats.docx_text(data).splitlines() if line]
    except Exception:  # noqa: BLE001 - a document that does not parse cannot be read
        return None
    if b"\x00" in data:
        return None
    return seen["data"]["quotes"]


def plan_text(text: str) -> bool:
    return bool(re.search(r'^- type:\s*"?plan"?\s*$', text, re.M))


def run_change(session: Session, number: str, slots: dict) -> dict:
    nas = session.nas
    if number == "D10":
        folder = to_sim(slots["memory_root"])
        text = slots["record_text"]
        fault = next((f for f in session.state["harness_faults"] if f["kind"] == "unverified_plan_save" and plan_text(text)), None)
        if folder is None:
            return {"state": "failed", "reason": "folder not found"}
        result = nas.save_text(folder, slots["record_file_hint"], text)
        if not result["ok"]:
            code = result["error"]["code"]
            return {"state": "cancelled" if code == "approval_declined" else "failed", "reason": code}
        data = result["data"]
        verified = data.get("verified", True) and fault is None
        return {"state": "completed", "result": {"saved_file": to_agent(data.get("outputFile")),
                                                 "verified": verified, "saved_bytes": data["contentBytes"]}}
    if number == "D11":
        created = []
        for path in [slots["recovery_folder"]] + slots["subfolder_list"]:
            sim = to_sim(path)
            if sim is None:
                return {"state": "failed", "reason": f"cannot create {path}", "created": created}
            result = nas.mkdir(sim)
            if not result["ok"]:
                code = result["error"]["code"]
                state = "cancelled" if code == "approval_declined" else "failed"
                return {"state": state, "reason": code, "path": path, "created": created}
            created.append(to_agent(result["data"]["realpath"]))
        return {"state": "completed", "result": {"created": created}}
    if number == "D12":
        src, dst = to_sim(slots["source_path"]), to_sim(slots["destination_path"])
        if src is None or dst is None:
            return {"state": "failed", "reason": "path not found"}
        result = nas.copy(src, dst)
        if not result["ok"]:
            code = result["error"]["code"]
            return {"state": "cancelled" if code == "approval_declined" else "failed", "reason": code}
        return {"state": "completed", "result": {"real_destination_path": to_agent(result["data"]["realpath"]),
                                                 "nas_result": "copied"}}
    raise ValueError(number)


def reveal_holdout(session: Session, hashed: list[str]) -> None:
    """Blind holdout: withheld TH- files appear only after a saved candidate policy file has been hashed."""
    withheld = session.state.get("withheld", {})
    if not withheld:
        return
    for path in hashed:
        sim = to_sim(path)
        data = session.nas.files.get(sim).data.decode("utf-8", "replace") if sim in session.nas.files else ""
        if re.search(r'^- type:\s*"policy"\s*$', data, re.M) and re.search(r'^- status:\s*"candidate"\s*$', data, re.M):
            for name, blob in withheld.items():
                session.nas.files[f"{session.state['memory_root']}/{name}"] = SimFile(base64.b64decode(blob), session.nas.clock)
            session.state["withheld"] = {}
            session.trace({"kind": "holdout_revealed", "after_hashing": path, "files": sorted(withheld)})
            return


def delegate(session: Session, target: str, instruction: str) -> dict:
    for number, (expected_target, pattern, names) in templates().items():
        match = pattern.fullmatch(instruction)
        if not match:
            continue
        if target != expected_target:
            return {"delegation": number, "state": "failed", "reason": f"{number} belongs to {expected_target}"}
        slots, problem = parse_slots(number, dict(zip(names, match.groups())))
        session.last_slots = slots
        if problem:
            return {"delegation": number, "state": "failed", "reason": f"instruction not understood: {problem}"}
        if number in STATE_CHANGES:
            session.state["approvals"] += 1
            approval = f"APV-{session.state['approvals']}"
            session.state["pending"][approval] = {"delegation": number, "slots": slots}
            return {"delegation": number, "state": "waiting_approval", "approval_id": approval,
                    "message": "The NAS asked the user to approve this change. Call resume with this approval_id."}
        result = run_read(session, number, slots)
        if number == "D7":
            reveal_holdout(session, slots["path_list"])
        if "failed" in result:
            return {"delegation": number, "state": "failed", "reason": result["failed"]}
        return {"delegation": number, "state": "completed", "result": result}
    return {"delegation": None, "state": "failed",
            "reason": "the expert did not recognize this instruction: use a delegate command written in SKILL.md"}


def resume(session: Session, approval: str) -> dict:
    pending = session.state["pending"].pop(approval, None)
    if pending is None:
        return {"state": "failed", "reason": "unknown or already answered approval"}
    number = pending["delegation"]
    decline = session.state["user"].get("nas_decline", [])
    session.decision = number not in decline
    outcome = run_change(session, number, pending["slots"])
    outcome.update(delegation=number, approval_id=approval, user_decision="granted" if session.decision else "declined")
    return outcome


def answer_user(session: Session, question: str) -> str:
    user = session.state["user"]
    plans = re.findall(r"PLN-\d{4}-\d{2}", question)
    digests = re.findall(r"\b[0-9a-f]{64}\b", question)
    short = re.findall(r"\b([0-9a-f]{4})(?:\.\.\.|…)([0-9a-f]{4})\b", question)
    lowered = question.lower()
    if plans and not (digests or short):
        if "save" in lowered:
            return ("Understood. Go ahead and save it; I will answer the NAS approval for the save. "
                    "I confirm a plan only by its ID and the digest of its saved file.")
        return "I confirm a plan only after it is saved, by its ID and the digest of its saved file."
    if plans:
        files = {p: f for p, f in session.nas.files.items() if f"## RECORD {plans[0]}" in f.data.decode("utf-8", "replace")}
        actual = {hashlib.sha256(f.data).hexdigest() for f in files.values()}
        shown = set(digests) | {d for d in actual for a, b in short if d.startswith(a) and d.endswith(b)}
        if not files:
            return f"I cannot find a saved plan {plans[0]} in the memory folder, so I do not approve anything."
        if not (shown & actual):
            return f"The digest you show does not match the saved file of {plans[0]}. I do not approve."
        if user.get("approve_plan", True):
            return f"Yes. I confirm the approved set you showed and I approve plan {plans[0]} with that digest."
        return f"No. I do not approve plan {plans[0]}. Do not create or copy anything."
    policy = re.search(r"\bpolicy\b", lowered) and re.search(r"\bapprove\b", lowered)
    if policy and "approve_policy" in user:
        names = re.findall(r"POL-\d{4}-[0-9A-Za-z]+", question)
        version = re.findall(r"\bv\d+\b", question)
        what = " ".join(names[:1] + version[:1]) or "this policy"
        return f"Yes. I approve {what}." if user["approve_policy"] else f"No. I do not approve {what}."
    test_cases = re.search(r"\btest[- ]cases?\b|\bholdout\b", lowered) and "test_cases_reply" in user
    if "outcome" in lowered and "confirm" in lowered and "confirm_outcome" in user:
        return user["confirm_outcome"] + (" " + user["test_cases_reply"] if test_cases else "")
    if test_cases:
        return user["test_cases_reply"]
    if "retire" in lowered and "retire_decision" in user:
        return user["retire_decision"]
    if "partial" in lowered or "another approved set" in lowered or "stop" in lowered:
        return {"proceed-partial": "Recover the available members of the target set as a partial recovery.",
                "stop": "Stop. Do not recover anything.",
                "alternative-set": "Recover the other approved set that is complete."}[user.get("on_partial", "proceed-partial")]
    return user.get("default_reply", "I have nothing to add. Continue only with what you can verify, or stop.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("delegate")
    d.add_argument("--target", required=True)
    text = d.add_mutually_exclusive_group(required=True)
    text.add_argument("--instruction")
    text.add_argument("--instruction-file", help="UTF-8 file holding the instruction; avoids local argument-length limits")
    r = sub.add_parser("resume")
    r.add_argument("--approval", required=True)
    a = sub.add_parser("ask-user")
    a.add_argument("--question", required=True)
    n = sub.add_parser("tell")
    n.add_argument("--message", required=True)
    f = sub.add_parser("finish")
    f.add_argument("--report-file", required=True)
    args = parser.parse_args(argv)
    session = Session(Path(args.session))
    if session.state.get("finished"):
        print(json.dumps({"state": "failed", "reason": "the session is finished"}))
        return 1
    if args.command == "delegate":
        instruction = args.instruction if args.instruction is not None else \
            Path(args.instruction_file).read_text(encoding="utf-8")
        out = delegate(session, args.target, instruction)
        session.trace({"kind": "delegate", "target": args.target, "instruction": instruction,
                       "transport": "file" if args.instruction is None else "argument",
                       "slots": getattr(session, "last_slots", None), "answer": out})
    elif args.command == "resume":
        out = resume(session, args.approval)
        session.trace({"kind": "resume", "approval": args.approval, "answer": out})
    elif args.command == "tell":
        out = {"state": "completed", "message": "notice shown to the user"}
        session.trace({"kind": "notice", "message": args.message})
    elif args.command == "ask-user":
        out = {"state": "completed", "user_reply": answer_user(session, args.question)}
        session.trace({"kind": "waiting_user", "question": args.question, "answer": out})
    else:
        text = Path(args.report_file).read_text(encoding="utf-8")
        session.state["finished"] = True
        out = {"state": "completed", "message": "final report recorded"}
        session.trace({"kind": "final_report", "text": text})
    session.save()
    print(json.dumps(out, ensure_ascii=True, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
