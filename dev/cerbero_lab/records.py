"""Writer, parser and validator for the cerbero-memory-2 bundle format of references/memory-records.md.

Every field line is `- key: <JSON value>`. Strings are JSON strings, lists are JSON arrays, pairs are
JSON objects, absent values are null. The encoding is reversible: parse(render(x)) returns exactly the
values that were added. Parsing is syntactic; validate() checks record types and required fields;
check_references() checks that every referenced record exists.
"""
from __future__ import annotations

import json
import re

SCHEMA = "cerbero-memory-2"
HEADER_FIELDS = ("schema", "bundle_id", "case_id", "scope_id", "supersedes")
_FIELD = re.compile(r"^- ([a-z0-9_]+): (.*)$")
_RECORD = re.compile(r"^## RECORD (\S+)$")
_TITLE = re.compile(r"^# CERBERO BUNDLE (\S+)$")
ID_PATTERN = re.compile(r"^[A-Z]{1,4}-[0-9]{4}(?:-[0-9A-Za-z]+)*$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
# json.dumps leaves these unescaped; str.splitlines() and some editors treat them as line breaks.
_LINE_BREAKS = {" ": "\\u2028", " ": "\\u2029", "\x85": "\\u0085"}

ASSET_STATES = ["intact", "intact-metadata", "moved", "altered", "missing", "informational-change", "unknown"]
ENTRY_STATUSES = ["verified", "already-present-verified", "failed-copy", "failed-verification",
                  "invalidated-source-changed", "conflict-destination-exists", "destination-differs",
                  "no-source", "fidelity-only", "cancelled", "not-attempted", "out-of-scope", "state-unknown"]
TARGET_KINDS = ["approved-set", "chosen-files", "full-rebuild"]
OVERALL = ["verified", "fidelity-only", "partial", "failed", "cancelled", "invalidated", "not-needed"]
CLASSES = ["observed", "user-declared", "document-stated", "official-guidance", "inferred", "contradicted", "unknown"]
STATUS = ["current", "needs-review", "superseded"]
CLAIM_KINDS = ["asset-state", "cause", "contradiction", "recoverability"]

# kind: text, path, sha256, int, bool, ref, refs, list, map, or enum:<a|b|...>; a trailing ? allows null.
RECORD_TYPES: dict[str, dict[str, str]] = {
    "scope": {"real_root": "path", "name": "text", "authorized_by": "ref", "newest_mtime": "int?"},
    "asset": {"scope_id": "ref", "name": "text", "recorded_path": "path", "importance": "enum:critical|ordinary",
              "declared_by": "ref", "current_version": "ref", "recorded_size": "int", "recorded_mtime": "int?",
              "observation": "ref"},
    "version": {"asset_id": "ref", "sha256": "sha256", "size_bytes": "int", "approved_by": "ref?", "observation": "ref"},
    "approved-set": {"name": "text", "members": "map", "approved_by": "ref", "status": "enum:" + "|".join(STATUS)},
    "location": {"real_root": "path", "memberships": "map", "unknown_kinds": "list", "provenance": "ref",
                 "inventory": "enum:complete|possibly-incomplete"},
    "domain": {"kind": "enum:volume|storage-pool|device|site", "label": "text", "parent": "ref?", "provenance": "ref"},
    "copy": {"version_id": "ref", "real_path": "path", "location_id": "ref", "sha256": "sha256?", "observation": "ref?",
             "access": "enum:readable|denied|unknown", "status": "enum:" + "|".join(STATUS)},
    "statement": {"text": "text", "given_in": "text", "class": "enum:user-declared"},
    "case": {"scope_id": "ref?", "request": "text", "status": "enum:open|closed", "opened_in": "text"},
    "check-card": {"doubt": "text", "decision": "text", "operation": "text", "outcomes": "text", "cost": "text",
                   "budget_left": "int"},
    "observation": {"check_card": "ref?", "agent": "text", "delegation": "text",
                    "state": "enum:completed|failed|cancelled|waiting_user|waiting_approval", "result": "text",
                    "coverage": "text", "observed_at": "text", "class": "enum:observed"},
    "claim": {"kind": "enum:" + "|".join(CLAIM_KINDS), "subject": "text", "statement": "text", "class": "enum:" + "|".join(CLASSES),
              "supports": "list", "contradicts": "list", "depends_on": "list", "status": "enum:" + "|".join(STATUS)},
    "hypothesis": {"subject": "text", "text": "text", "status": "enum:open|supported|refuted|undetermined",
                   "for": "list", "against": "list", "next_check": "text"},
    "open-item": {"subject": "text", "reason": "text", "needed_to_resolve": "text"},
    "finding": {"source": "text", "quote": "text", "kind": "text", "action_taken": "text"},
    "map": {"subject": "ref", "scenario": "text", "verdict": "enum:recoverable|not-recoverable|undetermined",
            "members": "map", "evidence_level": "text?", "unknowns": "list"},
    "plan": {"case_id": "ref", "revision": "int", "reference": "enum:approved-version|source-fidelity",
             "target_set": "ref?", "recovery_folder": "path", "goal": "text", "preconditions": "text",
             "success_conditions": "text", "risks": "text", "pending": "list", "previous_receipt": "ref?",
             "supersedes_plan": "ref?"},
    "plan-entry": {"plan_id": "ref", "asset_id": "ref?", "name": "text", "version_id": "ref?",
                   "expected_sha256": "sha256", "size_bytes": "int", "source_path": "path", "destination_path": "path"},
    "approval": {"plan_id": "ref", "plan_sha256": "sha256?", "decision": "enum:granted|declined|not-requested",
                 "statement": "text"},
    "receipt": {"plan_id": "ref", "plan_sha256": "sha256?", "overall": "enum:" + "|".join(OVERALL),
                "reference": "enum:approved-version|source-fidelity", "set_complete": "bool?", "coverage": "text",
                "pending": "list", "reason": "text?"},
    "receipt-entry": {"receipt_id": "ref", "entry_id": "ref?", "asset_id": "ref?", "version_id": "ref?",
                      "status": "enum:" + "|".join(ENTRY_STATUSES), "destination_path": "path?",
                      "source_sha256_before": "sha256?", "destination_sha256": "sha256?",
                      "source_sha256_after": "sha256?", "note": "text"},
    "test-case": {"kind": "enum:origin|similar|counterexample|insufficient", "split": "enum:development|holdout",
                  "facts": "text", "expected": "text", "source": "text"},
    "policy": {"version": "text", "status": "enum:candidate|evaluated|approved|active|retired|rejected",
               "condition": "text", "scope": "text", "effect": "list", "motivated_by": "ref",
               "drafted_from": "refs", "rule_sha256": "sha256?", "approval": "text?"},
    "evaluation": {"policy_id": "ref", "rule_sha256": "sha256?", "cases": "list",
                   "verdict": "enum:evaluated|rejected|not-evaluable"},
    "index-entry": {"file": "path", "bundle_id": "text", "sha256": "sha256?", "status": "enum:" + "|".join(STATUS)},
}
OPTIONAL_FIELDS = {"supersedes": "ref?", "asset_state": "enum:" + "|".join(ASSET_STATES), "located_at": "path?"}
# Written by every save since Skill 1.2.0; optional when reading, so that records saved by an earlier version
# still parse. A receipt without them has unknown delivery completeness and a possibly incomplete pending list.
TYPE_OPTIONAL: dict[str, dict[str, str]] = {
    "plan": {"target_kind": "enum:" + "|".join(TARGET_KINDS), "target_members": "list", "outside_target": "list",
             "fragments": "map"},
    "receipt": {"outside_target": "list"},
    "receipt-entry": {"name": "text", "source_path": "path?", "checks": "map"},
}
REQUIRED_SINCE_1_2 = {kind: sorted(set(fields) - {"fragments"}) for kind, fields in TYPE_OPTIONAL.items()}


def encode(value) -> str:
    if isinstance(value, (set, frozenset)):
        raise TypeError("sets have no defined order; pass a list")
    if isinstance(value, tuple):
        value = list(value)
    text = json.dumps(value, ensure_ascii=False)
    for char, escape in _LINE_BREAKS.items():
        text = text.replace(char, escape)
    return text


class Bundle:
    def __init__(self, bundle_id: str, case_id: str | None = None, scope_id: str | None = "SCP-0001",
                 supersedes: str | None = None):
        self.header = {"schema": SCHEMA, "bundle_id": bundle_id, "case_id": case_id,
                       "scope_id": scope_id, "supersedes": supersedes}
        self.records: list[tuple[str, dict]] = []

    def add(self, record_id: str, record_type: str, **fields) -> str:
        if any(rid == record_id for rid, _ in self.records):
            raise ValueError(f"duplicate record {record_id}")
        values = {"type": record_type}
        values.update(fields)
        self.records.append((record_id, values))
        return record_id

    def render(self) -> str:
        lines = [f"# CERBERO BUNDLE {self.header['bundle_id']}"]
        lines += [f"- {k}: {encode(v)}" for k, v in self.header.items()]
        for record_id, values in self.records:
            lines += ["", f"## RECORD {record_id}"]
            lines += [f"- {k}: {encode(v)}" for k, v in values.items()]
        return "\n".join(lines) + "\n"


def parse(text: str) -> dict:
    """Return {"header": {...}, "records": {record_id: fields}} with decoded values, or raise ValueError."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    title = _TITLE.match(lines[0].rstrip("\r")) if lines else None
    if not title:
        raise ValueError("not a Cerbero bundle")
    header: dict = {}
    records: dict[str, dict] = {}
    current: dict | None = None
    for number, raw in enumerate(lines[1:], start=2):
        line = raw.rstrip("\r")
        record = _RECORD.match(line)
        if record:
            record_id = record.group(1)
            if record_id in records:
                raise ValueError(f"line {number}: duplicate record {record_id}")
            current = records[record_id] = {}
            continue
        match = _FIELD.match(line)
        if match:
            key, encoded = match.groups()
            target = current if current is not None else header
            if key in target:
                raise ValueError(f"line {number}: duplicate field {key}")
            try:
                target[key] = json.loads(encoded)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number}: field {key} is not a JSON value ({exc.msg})") from None
        elif line.strip():
            raise ValueError(f"line {number}: unexpected line")
    if header.get("schema") != SCHEMA:
        raise ValueError(f"unsupported schema {header.get('schema')!r}; expected {SCHEMA}")
    missing = [f for f in HEADER_FIELDS if f not in header]
    extra = [f for f in header if f not in HEADER_FIELDS]
    if missing or extra:
        raise ValueError(f"bundle header: missing {missing}, unexpected {extra}")
    if header["bundle_id"] != title.group(1):
        raise ValueError("bundle title and bundle_id differ")
    return {"header": header, "records": records}


def _kind_ok(kind: str, value) -> bool:
    nullable = kind.endswith("?")
    kind = kind.rstrip("?")
    if value is None:
        return nullable
    if kind in ("text", "path"):
        return isinstance(value, str) and (kind == "text" or value != "")
    if kind == "sha256":
        return isinstance(value, str) and bool(SHA_PATTERN.match(value))
    if kind == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "bool":
        return isinstance(value, bool)
    if kind == "ref":
        return isinstance(value, str) and bool(ID_PATTERN.match(value))
    if kind == "refs":
        return isinstance(value, list) and all(isinstance(v, str) and ID_PATTERN.match(v) for v in value)
    if kind == "list":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if kind == "map":
        return isinstance(value, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in value.items())
    if kind.startswith("enum:"):
        return value in kind[5:].split("|")
    raise ValueError(f"unknown field kind {kind}")


def validate(records: dict[str, dict]) -> list[str]:
    """Problems with record types, required fields and value kinds; empty when the records are well formed."""
    problems = []
    for record_id, fields in records.items():
        if not ID_PATTERN.match(record_id):
            problems.append(f"{record_id}: malformed record ID")
        kind = fields.get("type")
        spec = RECORD_TYPES.get(kind)
        if spec is None:
            problems.append(f"{record_id}: unknown record type {kind!r}")
            continue
        for name, field_kind in spec.items():
            if name not in fields:
                problems.append(f"{record_id}: incomplete {kind} record, missing {name}")
            elif not _kind_ok(field_kind, fields[name]):
                problems.append(f"{record_id}: {name} is not a valid {field_kind}")
        optional = {**OPTIONAL_FIELDS, **TYPE_OPTIONAL.get(kind, {})}
        for name, value in fields.items():
            if name == "type" or name in spec:
                continue
            if name not in optional:
                problems.append(f"{record_id}: unexpected field {name} in a {kind} record")
            elif not _kind_ok(optional[name], value):
                problems.append(f"{record_id}: {name} is not a valid {optional[name]}")
    return problems


def missing_current_fields(records: dict[str, dict]) -> list[str]:
    """Fields that Skill 1.2.0 always writes but an earlier version did not (used to grade new saves)."""
    return [f"{rid}: {kind} record without {name}" for rid, r in records.items()
            for kind in [r.get("type")] for name in REQUIRED_SINCE_1_2.get(kind, []) if name not in r]


def references(fields: dict) -> list[str]:
    """Record IDs that one record points to, by field kind (refs inside free lists count when ID-shaped)."""
    spec = {**RECORD_TYPES.get(fields.get("type"), {}), **OPTIONAL_FIELDS, **TYPE_OPTIONAL.get(fields.get("type"), {})}
    found = []
    for name, value in fields.items():
        kind = spec.get(name, "").rstrip("?")
        if kind == "ref" and isinstance(value, str):
            found.append(value)
        elif kind == "refs" and isinstance(value, list):
            found += value
        elif kind == "list" and name in ("depends_on", "supports", "contradicts", "pending", "for", "against",
                                         "target_members", "outside_target"):
            found += [v for v in value if isinstance(v, str) and ID_PATTERN.match(v)]
        elif kind == "map" and name == "members":
            found += [v for pair in value.items() for v in pair if ID_PATTERN.match(v)]
        elif kind == "map" and name == "memberships":
            found += [v for v in value.values() if ID_PATTERN.match(v)]
    return found


def check_references(records: dict[str, dict], known: set[str] | frozenset = frozenset()) -> list[str]:
    """Dangling references: IDs pointed to by a record that exist neither in records nor in known."""
    problems = []
    for record_id, fields in records.items():
        for ref in references(fields):
            if ref not in records and ref not in known:
                problems.append(f"{record_id}: reference to missing record {ref}")
    return problems
