from gen_bundle import render, write_save, SQ

REQ = "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."
RF = "/data/studio/recovered/cerbero-recovery-CAS-0002"
SRC = "/data/studio/backups/aurora-2026-10-01/layout.indd"
DST = RF + "/layout.indd"
L6 = "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"

recs = []


def R(rid, typ, *pairs):
    recs.append((rid, [("type", typ)] + list(pairs)))


R("CAS-0002", "case", ("scope_id", "SCP-0001"), ("request", REQ), ("status", "open"), ("opened_in", "this session"))
R("STM-0002-0001", "statement", ("text", REQ), ("given_in", "this session"), ("class", "user-declared"))

cards = [
    ("CHK-0002-0001", "Does CERBERO-B-0001-01.md still match its index digest 6828..2259 (IDX-0001-01-0001)?", "whether the baseline records (SET-0001-0002, versions, copies) can be used as evidence", "D7 file-agent, plus the digest of CERBERO-IDX-0001-01.md for the end-of-session index", "match: records usable; differs: needs-review, no approved reference", "2 digests, about 21 KB, read-only", 300),
    ("CHK-0002-0002", "Are the 11 recorded assets of SCP-0001 present at their recorded paths with the recorded size and modification time?", "which assets need digest checks and which are missing and need search or recovery", "D5 file-agent on the 11 recorded paths, all canonical and inside /data/studio/projects/aurora", "absent: test moved, copy elsewhere, no copy, not visible; present with equal metadata: D7 for critical assets; different metadata: D7", "metadata only, read-only", 298),
    ("CHK-0002-0003", "Was layout.indd (VER-0001-0006, 16384 bytes) moved or renamed inside the project?", "moved inside scope: report the new path and do not copy; not found: recover from a copy", "D6 file-agent, search_root /data/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200", "candidates: D7 against 84a4..1e1b; empty and complete: moved inside scope refuted to depth 8; possibly incomplete: split with D13", "1 size-filtered listing, read-only", 298),
    ("CHK-0002-0004", "Does the recorded copy CPY-0001-0015 (/data/studio/backups/aurora-2026-10-01/layout.indd) still exist inside its location root?", "whether it can be the recovery source of layout.indd", "D5 file-agent on a path from memory, canonical and inside the LOC-0001-0002 root", "present inside the root with 16384 bytes: D7; absent or outside: next candidate, then search the other named locations", "metadata only, read-only", 298),
    ("CHK-0002-0005", "Are brief.pdf, copy.docx, cover.tif and logo.ai still their Delivery 2 versions, and is the backup copy of layout.indd still VER-0001-0006?", "which set members need recovery, and whether CPY-0001-0015 is a valid source", "D7 file-agent on 5 files with expected digests", "match: intact or eligible source; differs: altered or candidate rejected, search the other named locations", "5 digests, about 67.6 KB, read-only", 298),
]
for cid, d, dec, op, out, cost, b in cards:
    R(cid, "check-card", ("doubt", d), ("decision", dec), ("operation", op), ("outcomes", out), ("cost", cost), ("budget_left", b))


def O(oid, card, deleg, result, cov):
    R(oid, "observation", ("check_card", card), ("agent", "file-agent"), ("delegation", deleg), ("state", "completed"), ("result", result), ("coverage", cov), ("observed_at", "unknown"), ("class", "observed"))


O("OBS-0002-0001", None, "D1", "user folder real path /data/studio", "1 of 1")
O("OBS-0002-0002", None, "D2", "7 of 7 folders exist and are readable, real path equal to the given path: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio", "7 of 7")
O("OBS-0002-0003", None, "D3", "2 files: /data/studio/cerbero-memory/CERBERO-B-0001-01.md 20942 bytes mtime 3001; /data/studio/cerbero-memory/CERBERO-IDX-0001-01.md 380 bytes mtime 3002", "2 entries, truncated false")
O("OBS-0002-0004", None, "D4", "2 files returned in full: CERBERO-IDX-0001-01.md, CERBERO-B-0001-01.md", "2 of 2, none reported partial")
O("OBS-0002-0005", "CHK-0002-0001", "D7", "/data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 682855fb8e2e81be54754163486d42504ac98e272ed3d002cef9a7ae8cd62259 20942 bytes, matches index entry IDX-0001-01-0001; /data/studio/cerbero-memory/CERBERO-IDX-0001-01.md sha256 4cf8bbe0ec55f7ec826eb8c5ceba33f042467747e2c07d7b88ba977f86ec7e0b 380 bytes", "2 of 2 files hashed")
O("OBS-0002-0006", "CHK-0002-0002", "D5", "10 of 11 recorded asset paths exist, readable, real path equal to the recorded path, size and mtime equal to the recorded values (brief.pdf 4096/1100, copy.docx 6144/1102, cover.tif 32768/1103, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, logo.ai 8192/900, palette.ase 512/900, raw/DSC_0101.ARW 65536/800, raw/DSC_0142.ARW 65536/801, raw/DSC_0150.ARW 65536/802); /data/studio/projects/aurora/layout.indd exists false, reason not_found", "11 of 11 paths checked by metadata")
O("OBS-0002-0007", "CHK-0002-0003", "D6", "under /data/studio/projects/aurora, depth 8, regular files of exactly 16384 bytes: 0 files, truncated false, no unreadable subfolders", "complete to depth 8: 0 entries of limit 200, truncation reported absent, no unreadable subfolder")
O("OBS-0002-0008", "CHK-0002-0004", "D5", "/data/studio/backups/aurora-2026-10-01/layout.indd exists, readable, real path /data/studio/backups/aurora-2026-10-01/layout.indd, 16384 bytes, mtime 1200", "1 of 1")
O("OBS-0002-0009", "CHK-0002-0005", "D7", "/data/studio/backups/aurora-2026-10-01/layout.indd 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b 16384 bytes matches VER-0001-0006; /data/studio/projects/aurora/brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 bytes matches VER-0001-0001; /data/studio/projects/aurora/copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes matches VER-0001-0002; /data/studio/projects/aurora/cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes matches VER-0001-0003; /data/studio/projects/aurora/logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes matches VER-0001-0007", "5 of 5 files hashed")


def C(cid, subj, state, loc, stmt, cls, sup, contra, dep):
    R(cid, "claim", ("kind", "asset-state"), ("subject", subj), ("asset_state", state), ("located_at", loc), ("statement", stmt), ("class", cls), ("supports", sup), ("contradicts", contra), ("depends_on", dep), ("status", "current"))


C("CLM-0002-0001", "AST-0001-0006", "missing", None, "layout.indd is absent at /data/studio/projects/aurora/layout.indd; no file of 16384 bytes exists in the project to depth 8 (search complete); cause unknown", "observed", ["OBS-0002-0006", "OBS-0002-0007"], [], ["AST-0001-0006", "VER-0001-0006", "/data/studio/projects/aurora/layout.indd absent (OBS-0002-0006)"])
for cid, ast, ver, name, dg in [
    ("CLM-0002-0002", "AST-0001-0001", "VER-0001-0001", "brief.pdf", "9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"),
    ("CLM-0002-0003", "AST-0001-0002", "VER-0001-0002", "copy.docx", "0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"),
    ("CLM-0002-0004", "AST-0001-0003", "VER-0001-0003", "cover.tif", "2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"),
    ("CLM-0002-0005", "AST-0001-0007", "VER-0001-0007", "logo.ai", "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"),
]:
    p = "/data/studio/projects/aurora/" + name
    C(cid, ast, "intact", p, name + " at its recorded path has the digest of Delivery 2 version " + ver, "observed", ["OBS-0002-0006", "OBS-0002-0009"], [], [ast, ver, p + " sha256 " + dg])
n = 6
for ast, rel in [("AST-0001-0004", "exports/previews/cover-preview.jpg"), ("AST-0001-0005", "fonts-license.pdf"), ("AST-0001-0008", "palette.ase"),
                 ("AST-0001-0009", "raw/DSC_0101.ARW"), ("AST-0001-0010", "raw/DSC_0142.ARW"), ("AST-0001-0011", "raw/DSC_0150.ARW")]:
    p = "/data/studio/projects/aurora/" + rel
    C("CLM-0002-%04d" % n, ast, "intact-metadata", p, rel + " present with recorded size and mtime; content not hashed in this session", "observed", ["OBS-0002-0006"], [], [ast, p + " metadata (OBS-0002-0006)"])
    n += 1

R("CLM-0002-0012", "claim", ("kind", "contradiction"), ("subject", "CPY-0001-0006"), ("statement", "copy record CPY-0001-0006 (OBS-0001-0006) places VER-0001-0006 at /data/studio/projects/aurora/layout.indd; D5 in this session reports that path not_found (OBS-0002-0006)"), ("class", "contradicted"), ("supports", ["OBS-0002-0006"]), ("contradicts", ["CPY-0001-0006"]), ("depends_on", ["CPY-0001-0006", "OBS-0002-0006"]), ("status", "current"))
R("CPY-0002-0001", "copy", ("version_id", "VER-0001-0006"), ("real_path", "/data/studio/projects/aurora/layout.indd"), ("location_id", "LOC-0001-0001"), ("sha256", None), ("observation", "OBS-0002-0006"), ("access", "unknown"), ("status", "needs-review"), ("supersedes", "CPY-0001-0006"))
R("CLM-0002-0013", "claim", ("kind", "copy-verification"), ("subject", "CPY-0001-0015"), ("statement", "copy CPY-0001-0015 at /data/studio/backups/aurora-2026-10-01/layout.indd re-observed in this session with the digest of VER-0001-0006 (evidence level verified-now); its 16384-byte size and real path inside LOC-0001-0002 were confirmed first"), ("class", "observed"), ("supports", ["OBS-0002-0008", "OBS-0002-0009"]), ("contradicts", []), ("depends_on", ["CPY-0001-0015", "VER-0001-0006", SRC + " sha256 " + L6]), ("status", "current"))


def H(hid, text, st, fo, ag, nx):
    R(hid, "hypothesis", ("subject", "AST-0001-0006"), ("text", text), ("status", st), ("for", fo), ("against", ag), ("next_check", nx))


H("HYP-0002-0001", "layout.indd was moved or renamed inside the project with unchanged content", "refuted", [], ["OBS-0002-0007"], "none: exact-size search complete to depth 8")
H("HYP-0002-0002", "layout.indd is absent from the project and a copy of VER-0001-0006 exists in a named location", "supported", ["OBS-0002-0006", "OBS-0002-0007", "OBS-0002-0009"], [], "none")
H("HYP-0002-0003", "layout.indd is absent and no copy of VER-0001-0006 exists", "refuted", [], ["OBS-0002-0009"], "none")
H("HYP-0002-0004", "layout.indd is present but not visible to this account", "undetermined", [], ["OBS-0002-0006", "OBS-0002-0007"], "none available in the capability evidence: D5 reported not_found rather than unreadable and D6 named no unreadable subfolder")
H("HYP-0002-0005", "an edited version of layout.indd with a different size exists under another name in the project", "open", [], [], "one D6 listing of the project of any size; not run because the user did not ask what happened and its result would not change the recovery of VER-0001-0006")
R("OPN-0002-0001", "open-item", ("subject", "AST-0001-0006"), ("reason", "cause of the disappearance of layout.indd is unknown; no source states it"), ("needed_to_resolve", "a user statement or a cited project document that states it"))
R("OPN-0002-0002", "open-item", ("subject", "SCP-0001"), ("reason", "the project folder was not listed in full in this session; new or renamed files of other sizes were not reviewed"), ("needed_to_resolve", "one D6 listing of /data/studio/projects/aurora of any size"))

goal = ("Recover approved set SET-0001-0002 (Delivery 2) member layout.indd, version VER-0001-0006 (sha256 " + L6 + ", 16384 bytes), into the new folder " + RF + ". "
        "Target set members: brief.pdf VER-0001-0001, layout.indd VER-0001-0006, copy.docx VER-0001-0002, cover.tif VER-0001-0003, logo.ai VER-0001-0007; record file /data/studio/cerbero-memory/CERBERO-B-0001-01.md; approving statement STM-0001-0005. "
        "The other four members were observed intact in this session (CLM-0002-0002 to CLM-0002-0005) and are not copied. "
        "Operations: create " + RF + " with no subfolders; copy, never move, never overwrite, " + SRC + " to " + DST + ".")
pre = ("The user confirmed plan PLN-0002-01, its saved digest and target set SET-0001-0002 in this session; mkdir and cpmv in copy mode without overwrite are in the capability evidence and the expert reports them allowed; "
       "the saved plan file, hashed again immediately before the first change, has the confirmed digest; "
       "the source real path lies inside /data/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals " + L6 + "; "
       "the destination does not exist and lies inside " + RF + "; the NAS approval of the folder and of the copy is answered by the user.")
succ = ("The folder exists at the real path " + RF + " returned by the NAS; the copy exists at the planned real path " + DST + " returned by the NAS; its digest equals " + L6 + ".")
risks = ("Single eligible source (CPY-0001-0015), on Volume 2 of this NAS per STM-0001-0003; the source may change before or during the copy (it is hashed before, and again if the destination differs); the copy is not atomic; "
         "memory, copies and digests are on the same NAS and are not an independent root of trust; the cause of the disappearance is unknown (OPN-0002-0001); the project was not listed in full (OPN-0002-0002).")
R("PLN-0002-01", "plan", ("case_id", "CAS-0002"), ("revision", 1), ("reference", "approved-version"), ("target_set", "SET-0001-0002"), ("recovery_folder", RF), ("goal", goal), ("preconditions", pre), ("success_conditions", succ), ("risks", risks), ("pending", []), ("previous_receipt", None), ("supersedes_plan", None))
R("ENT-0002-01-01", "plan-entry", ("plan_id", "PLN-0002-01"), ("asset_id", "AST-0001-0006"), ("name", "layout.indd"), ("version_id", "VER-0001-0006"), ("expected_sha256", L6), ("size_bytes", 16384), ("source_path", SRC), ("destination_path", DST))

text = render("B-0002-01", "CAS-0002", "SCP-0001", recs)
with open("bundle_B-0002-01.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
write_save("B-0002-01", text, "d10_B-0002-01.sh")
print(len(text.encode("utf-8")), "bytes;", len(recs), "records; single quotes:", text.count(SQ))
