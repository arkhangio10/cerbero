import json
J = lambda v: json.dumps(v, ensure_ascii=False)
out = []
def f(k, v): out.append(f"- {k}: {J(v)}")
def rec(rid, typ, **fields):
    out.append(""); out.append(f"## RECORD {rid}"); f("type", typ)
    for k, v in fields.items(): f(k, v)

out.append("# CERBERO BUNDLE B-0002-01")
f("schema", "cerbero-memory-2"); f("bundle_id", "B-0002-01"); f("case_id", "CAS-0002"); f("scope_id", "SCP-0001"); f("supersedes", None)
REQ = "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /volume1/studio/projects/aurora. Cerbero memory folder: /volume1/studio/cerbero-memory. Copy locations: /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora. Create the recovery folder under /volume1/studio/recovered."
rec("CAS-0002", "case", scope_id="SCP-0001", request=REQ, status="open", opened_in="this session")
rec("STM-0002-0001", "statement", text=REQ, given_in="this session", **{"class": "user-declared"})
rec("STM-0002-0002", "statement", text="Recover the available members of the target set as a partial recovery.", given_in="this session, reply to the choice between stopping, recovering Delivery 1 or naming another location", **{"class": "user-declared"})

def obs(rid, chk, agent, dlg, state, result, coverage):
    rec(rid, "observation", check_card=chk, agent=agent, delegation=dlg, state=state, result=result, coverage=coverage, observed_at="unknown", **{"class": "observed"})
def chk(rid, doubt, decision, op, outcomes, cost, left):
    rec(rid, "check-card", doubt=doubt, decision=decision, operation=op, outcomes=outcomes, cost=cost, budget_left=left)

obs("OBS-0002-0001", None, "file-agent", "D1", "completed", "user folder real_path /volume1/studio", "1 path")
obs("OBS-0002-0002", None, "file-agent", "D2", "completed", "projects/aurora, cerbero-memory, backups/aurora-2026-11-05, usb-archive/aurora and recovered under /volume1/studio: exist, readable, real_path equal to the named path; /volume1/studio/backups/aurora-2026-10-01: exists, readable, no real_path returned; /volume1/studio: exists false, reason not found", "7 folders")
obs("OBS-0002-0003", None, "file-agent", "D3", "completed", "2 files: /volume1/studio/cerbero-memory/CERBERO-B-0001-01.md 20963 bytes mtime 3001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md 383 bytes mtime 3002", "truncated false")
obs("OBS-0002-0004", None, "file-agent", "D4", "completed", "CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md returned in full; B-0001-01 parses as cerbero-memory-2 with 79 records", "2 of 2 files, no partial read reported")
obs("OBS-0002-0005", None, "file-agent", "D7", "completed", "CERBERO-B-0001-01.md sha256 0589d203a592b05653d6b2c36b37879bd62506966497a4ecc54c887061744c0d 20963 bytes, equal to IDX-0001-01-0001; CERBERO-IDX-0001-01.md sha256 d48d2e2b404273c949663bc149a568d1f42a680b6c73f73cf1576fa37bfbf41b 383 bytes", "2 of 2 files hashed")

chk("CHK-0002-0001", "Are the 11 recorded assets present at their recorded paths with the recorded size and time?", "which assets need digests and which need a search", "D5 file-agent", "missing: search hypotheses; size or time differ: D7; same: D7 for critical assets and set members, intact-metadata for ordinary assets", "metadata of 11 paths, read-only", 298)
obs("OBS-0002-0006", "CHK-0002-0001", "file-agent", "D5", "completed", "brief.pdf 4096 mtime 1100; copy.docx 6144 mtime 1102; cover.tif 32768 mtime 1103; exports/previews/cover-preview.jpg 4096 mtime 1104; fonts-license.pdf 2048 mtime 900; logo.ai 8192 mtime 900; palette.ase 512 mtime 900, all with real_path equal to the recorded path; layout.indd exists false, reason not_found; raw/DSC_0101.ARW, raw/DSC_0142.ARW and raw/DSC_0150.ARW exists false, reason permission_denied", "11 of 11 paths answered")
chk("CHK-0002-0002", "Are brief.pdf, copy.docx, cover.tif and logo.ai in the project still the Delivery 2 versions?", "whether any Delivery 2 member besides layout.indd needs recovery", "D7 file-agent with the expected digests of VER-0001-0001, VER-0001-0002, VER-0001-0003 and VER-0001-0007", "match: intact; differ: altered and added to the recovery", "4 digests, 51200 bytes, read-only", 298)
obs("OBS-0002-0007", "CHK-0002-0002", "file-agent", "D7", "completed", "brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 match; copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 match; cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 match; logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 match", "4 of 4 files hashed")
chk("CHK-0002-0003", "Was layout.indd moved or renamed inside the project?", "moved inside the scope (no copy needed) or absent (recover)", "D6 file-agent on /volume1/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200", "candidates: D7 against VER-0001-0006; empty and complete: not relocated in scope", "1 listing, read-only", 294)
obs("OBS-0002-0008", "CHK-0002-0003", "file-agent", "D6", "completed", "empty list; truncated false; unreadable subfolder /volume1/studio/projects/aurora/raw", "possibly incomplete: raw unreadable")
chk("CHK-0002-0004", "Which parts of the project search are incomplete, and can raw be searched on its own?", "whether the relocation hypothesis can be closed", "D13 file-agent on /volume1/studio/projects/aurora", "raw readable: D6 in each subfolder; unreadable: not reviewed", "1 listing, read-only", 294)
obs("OBS-0002-0009", "CHK-0002-0004", "file-agent", "D13", "completed", "subfolders /volume1/studio/projects/aurora/exports and /volume1/studio/projects/aurora/raw; truncated false; no unreadable subfolder named", "depth 1")
chk("CHK-0002-0005", "Is a 16384-byte file inside raw or exports?", "close or keep the relocation hypothesis", "D6 file-agent on each subfolder returned by D13, size exactly 16384 bytes, depth 8, limit 200", "candidates: D7; empty and complete: not relocated there", "2 listings, read-only", 294)
obs("OBS-0002-0010", "CHK-0002-0005", "file-agent", "D6", "failed", "search under /volume1/studio/projects/aurora/raw failed, reason permission_denied", "raw not reviewed")
obs("OBS-0002-0011", "CHK-0002-0005", "file-agent", "D6", "completed", "search under /volume1/studio/projects/aurora/exports: empty list; truncated false; no unreadable subfolder", "complete to depth 8")
chk("CHK-0002-0006", "What is the real path of /volume1/studio/backups/aurora-2026-10-01, for which the first D2 returned none?", "whether CPY-0001-0015, the only other recorded copy of VER-0001-0006, can be re-checked as a source", "D2 file-agent, 1 folder", "canonical real path: authorized root, then D5 and D7 on CPY-0001-0015; none: the location cannot be used", "metadata, read-only", 294)
obs("OBS-0002-0012", "CHK-0002-0006", "file-agent", "D2", "completed", "/volume1/studio/backups/aurora-2026-10-01 exists true, readable true, no real_path returned", "1 folder")
chk("CHK-0002-0007", "Does backups/aurora-2026-11-05 or usb-archive/aurora hold a 16384-byte file that could be VER-0001-0006?", "which source, if any, can serve layout.indd for Delivery 2", "D6 file-agent on each location, size exactly 16384 bytes, depth 8, limit 200", "candidates: D5 and D7 against VER-0001-0006; empty and complete: no copy of that version there", "2 listings, read-only", 294)
obs("OBS-0002-0013", "CHK-0002-0007", "file-agent", "D6", "completed", "search under /volume1/studio/backups/aurora-2026-11-05: empty list; truncated false; no unreadable subfolder", "complete to depth 8")
obs("OBS-0002-0014", "CHK-0002-0007", "file-agent", "D6", "completed", "search under /volume1/studio/usb-archive/aurora: empty list; truncated false; no unreadable subfolder", "complete to depth 8")

def claim(rid, kind, subject, statement, cls, supports, contradicts, depends, state=None, loc=None, has_state=False):
    d = dict(kind=kind, subject=subject, statement=statement)
    d["class"] = cls
    d.update(supports=supports, contradicts=contradicts, depends_on=depends, status="current")
    if has_state:
        d["asset_state"] = state; d["located_at"] = loc
    rec(rid, "claim", **d)

P = "/volume1/studio/projects/aurora/"
claim("CLM-0002-0001", "asset-state", "AST-0001-0001", "brief.pdf at its recorded path equals approved version VER-0001-0001 (Delivery 2)", "observed", ["OBS-0002-0007"], [], ["VER-0001-0001", "OBS-0002-0007", P + "brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"], "intact", P + "brief.pdf", True)
claim("CLM-0002-0002", "asset-state", "AST-0001-0002", "copy.docx at its recorded path equals approved version VER-0001-0002 (Delivery 2)", "observed", ["OBS-0002-0007"], [], ["VER-0001-0002", "OBS-0002-0007", P + "copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"], "intact", P + "copy.docx", True)
claim("CLM-0002-0003", "asset-state", "AST-0001-0003", "cover.tif at its recorded path equals approved version VER-0001-0003 (Delivery 2)", "observed", ["OBS-0002-0007"], [], ["VER-0001-0003", "OBS-0002-0007", P + "cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"], "intact", P + "cover.tif", True)
claim("CLM-0002-0004", "asset-state", "AST-0001-0007", "logo.ai at its recorded path equals approved version VER-0001-0007 (Delivery 1 and Delivery 2)", "observed", ["OBS-0002-0007"], [], ["VER-0001-0007", "OBS-0002-0007", P + "logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"], "intact", P + "logo.ai", True)
claim("CLM-0002-0005", "asset-state", "AST-0001-0006", "layout.indd is missing at its recorded path; the in-scope search is incomplete because raw is unreadable; cause unknown", "observed", ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0010", "OBS-0002-0011"], [], ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0010", "OBS-0002-0011"], "missing", None, True)
claim("CLM-0002-0006", "asset-state", "AST-0001-0004", "cover-preview.jpg has the recorded size and time; content not hashed", "observed", ["OBS-0002-0006"], [], ["OBS-0002-0006"], "intact-metadata", P + "exports/previews/cover-preview.jpg", True)
claim("CLM-0002-0007", "asset-state", "AST-0001-0005", "fonts-license.pdf has the recorded size and time; content not hashed", "observed", ["OBS-0002-0006"], [], ["OBS-0002-0006"], "intact-metadata", P + "fonts-license.pdf", True)
claim("CLM-0002-0008", "asset-state", "AST-0001-0008", "palette.ase has the recorded size and time; content not hashed", "observed", ["OBS-0002-0006"], [], ["OBS-0002-0006"], "intact-metadata", P + "palette.ase", True)
for i, (a, n) in enumerate([("AST-0001-0009", "DSC_0101.ARW"), ("AST-0001-0010", "DSC_0142.ARW"), ("AST-0001-0011", "DSC_0150.ARW")]):
    claim(f"CLM-0002-{9 + i:04d}", "asset-state", a, f"raw/{n} could not be checked: permission_denied", "observed", ["OBS-0002-0006"], [], ["OBS-0002-0006"], "unknown", None, True)
claim("CLM-0002-0012", "contradiction", "CPY-0001-0006", "Copy record CPY-0001-0006 places VER-0001-0006 at /volume1/studio/projects/aurora/layout.indd as readable; D5 in this session reports that path not_found", "contradicted", ["OBS-0002-0006"], ["CPY-0001-0006"], ["CPY-0001-0006", "OBS-0002-0006"])
claim("CLM-0002-0013", "contradiction", "/volume1/studio", "D1 returned /volume1/studio as the real path of the user folder; D2 in the same session reported /volume1/studio as not found", "contradicted", ["OBS-0002-0001"], ["OBS-0002-0002"], ["OBS-0002-0001", "OBS-0002-0002"])
claim("CLM-0002-0014", "contradiction", "/volume1/studio/projects/aurora/raw", "D13 listed raw and named no unreadable subfolder; D6 named raw unreadable and a D6 inside raw failed with permission_denied", "contradicted", ["OBS-0002-0008", "OBS-0002-0010"], ["OBS-0002-0009"], ["OBS-0002-0008", "OBS-0002-0009", "OBS-0002-0010"])
claim("CLM-0002-0015", "source-availability", "VER-0001-0006", "No eligible source for layout.indd version VER-0001-0006 (Delivery 2) in the locations resolved this session; the only other recorded copy, CPY-0001-0015, lies in a location whose real path the NAS did not return, so it was not read", "observed", ["OBS-0002-0002", "OBS-0002-0006", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"], [], ["CPY-0001-0015", "LOC-0001-0002", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"])

def cpy(rid, ver, path, access, old):
    rec(rid, "copy", version_id=ver, real_path=path, location_id="LOC-0001-0001", sha256=None, observation="OBS-0002-0006", access=access, status="needs-review", supersedes=old)
cpy("CPY-0002-0001", "VER-0001-0006", P + "layout.indd", "unknown", "CPY-0001-0006")
cpy("CPY-0002-0002", "VER-0001-0009", P + "raw/DSC_0101.ARW", "denied", "CPY-0001-0009")
cpy("CPY-0002-0003", "VER-0001-0010", P + "raw/DSC_0142.ARW", "denied", "CPY-0001-0010")
cpy("CPY-0002-0004", "VER-0001-0011", P + "raw/DSC_0150.ARW", "denied", "CPY-0001-0011")

def hyp(rid, subj, text, status, fr, ag, nxt):
    rec(rid, "hypothesis", subject=subj, text=text, status=status, **{"for": fr}, against=ag, next_check=nxt)
hyp("HYP-0002-0001", "AST-0001-0006", "layout.indd was moved or renamed inside the project", "open", [], ["OBS-0002-0008", "OBS-0002-0011"], "D6 for 16384-byte files under /volume1/studio/projects/aurora/raw once it is readable, then D7 on candidates")
hyp("HYP-0002-0002", "AST-0001-0006", "layout.indd is absent from the project and VER-0001-0006 has a copy elsewhere", "undetermined", ["CPY-0001-0015"], ["OBS-0002-0013", "OBS-0002-0014"], "a D2 result with the real path of /volume1/studio/backups/aurora-2026-10-01, then D5 and D7 on CPY-0001-0015")
hyp("HYP-0002-0003", "AST-0001-0006", "layout.indd is absent and VER-0001-0006 has no copy in any named location", "open", ["OBS-0002-0013", "OBS-0002-0014"], [], "the same check as HYP-0002-0002")
hyp("HYP-0002-0004", "AST-0001-0006", "layout.indd exists at its path but is not visible to the expert", "open", [], ["OBS-0002-0006"], "none available to Cerbero; D5 reported not_found, not permission_denied")

def opn(rid, subj, reason, need):
    rec(rid, "open-item", subject=subj, reason=reason, needed_to_resolve=need)
opn("OPN-0002-0001", "LOC-0001-0002", "D2 confirmed /volume1/studio/backups/aurora-2026-10-01 exists and is readable but returned no real path, twice; containment of CPY-0001-0015 cannot be shown, so it was not read", "a completed D2 that returns the real path of that folder, or another readable location named by the user")
opn("OPN-0002-0002", "/volume1/studio/projects/aurora/raw", "permission_denied for D5 on three raw files and for D6 inside raw", "read access to raw for the NAS expert, granted by the user or an administrator")
opn("OPN-0002-0003", "AST-0001-0006", "layout.indd version VER-0001-0006 (Delivery 2) was not recovered: no eligible source; the partial recovery the user chose (STM-0002-0002) had no member with a source, so no plan was written, no folder was created and nothing was copied", "resolve OPN-0002-0001 or name another location that holds VER-0001-0006, then a new recovery plan")

text = "\n".join(out) + "\n"
assert "'" not in text
open("scratch_B-0002-01.md", "w", encoding="utf-8", newline="\n").write(text)
print(len(text.encode("utf-8")), "bytes;", sum(1 for l in out if l.startswith("## RECORD")), "records")
