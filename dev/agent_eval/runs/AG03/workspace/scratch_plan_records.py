BUNDLE_ID = "B-0002-01"
CASE_ID = "CAS-0002"
SCOPE_ID = "SCP-0001"
HINT = "CERBERO-B-0002-01"
OUT_MD = "plan_bundle.md"
OUT_SH = "d10_plan.sh"

REQ = "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."
V6 = "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
RF = "/data/studio/recovered/cerbero-recovery-CAS-0002"
RECS = []


def R(rid, **f):
    RECS.append((rid, f))


R("CAS-0002", type="case", scope_id="SCP-0001", request=REQ, status="open", opened_in="this session")
R("STM-0002-0001", type="statement", text=REQ, given_in="this session", class_="user-declared")

cards = [
    ("CHK-0002-0001", "Does bundle B-0001-01 still match its digest in index IDX-0001-01?", "whether the baseline records can be used as evidence", "D7 file-agent on /data/studio/cerbero-memory/CERBERO-B-0001-01.md", "match: records usable; differ: needs-review, no baseline", "1 digest of 20964 bytes, read-only", 300),
    ("CHK-0002-0002", "Are the 10 in-scope assets present at their recorded paths with the recorded size and time?", "which assets need a digest check and which are missing; AST-0001-0001 excluded because its recorded path is not canonical", "D5 file-agent on 10 recorded asset paths", "present and unchanged: D7 for critical assets, intact-metadata for ordinary; changed: D7; missing: D6 exact-size search", "metadata of 10 paths, read-only", 299),
    ("CHK-0002-0003", "Are copy.docx, cover.tif and logo.ai at their recorded paths still the Delivery 2 versions?", "whether these Delivery 2 members need recovery", "D7 file-agent on 3 files with expected digests of VER-0001-0002, VER-0001-0003, VER-0001-0007", "match: intact; differ: altered, recover", "3 digests, 47104 bytes, read-only", 299),
    ("CHK-0002-0004", "Was layout.indd moved or renamed inside the project?", "whether layout.indd needs a copy from another location", "D6 file-agent under /data/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200", "candidates: D7 against VER-0001-0006; complete empty list: hypothesis moved-in-scope refuted", "1 size-filtered listing, read-only", 296),
    ("CHK-0002-0005", "Does any named copy location hold a 16384-byte file that could be layout.indd version VER-0001-0006?", "whether a source exists for VER-0001-0006", "D6 file-agent under each of the 3 copy locations, size exactly 16384 bytes, depth 8, limit 200", "candidates: D7 against VER-0001-0006; no candidate in complete listings: no source with the available locations", "3 size-filtered listings, read-only", 296),
    ("CHK-0002-0006", "Is /data/studio/backups/aurora-2026-10-01/layout.indd the Delivery 2 version VER-0001-0006?", "whether it can be the recovery source", "D7 file-agent on 1 file with expected digest of VER-0001-0006", "match: eligible source re-observed now; differ: no source for VER-0001-0006", "1 digest of 16384 bytes, read-only", 296),
]
for c in cards:
    R(c[0], type="check-card", doubt=c[1], decision=c[2], operation=c[3], outcomes=c[4], cost=c[5], budget_left=c[6])

obs = [
    ("OBS-0002-0001", None, "D1", "user folder real path /data/studio", "1 of 1"),
    ("OBS-0002-0002", None, "D2", "7 folders exist and are readable with real paths equal to the given paths: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio", "7 of 7 folders"),
    ("OBS-0002-0003", None, "D3", "2 CERBERO- files: CERBERO-B-0001-01.md 20964 bytes, CERBERO-IDX-0001-01.md 380 bytes; truncated false", "2 entries, not truncated"),
    ("OBS-0002-0004", None, "D4", "full text of CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md returned; no file reported missing, unreadable or partial", "2 of 2 files"),
    ("OBS-0002-0005", "CHK-0002-0001", "D7", "/data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 22d927d38eabd5a2be1748dc9df31b3e09a4b524db937a5f386771d06dc1e19a, 20964 bytes, matches index entry IDX-0001-01-0001", "1 of 1 files hashed"),
    ("OBS-0002-0006", "CHK-0002-0002", "D5", "layout.indd not found (reason not_found); copy.docx 6144 mtime 1102, cover.tif 32768 mtime 1103, cover-preview.jpg 4096 mtime 1104, fonts-license.pdf 2048 mtime 900, logo.ai 8192 mtime 900, palette.ase 512 mtime 900, DSC_0101.ARW 65536 mtime 800, DSC_0142.ARW 65536 mtime 801, DSC_0150.ARW 65536 mtime 802, all present, readable, real path equal to recorded path, size and time equal to the asset records", "10 of 10 paths answered"),
    ("OBS-0002-0007", "CHK-0002-0003", "D7", "copy.docx sha256 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes matches; cover.tif sha256 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes matches; logo.ai sha256 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes matches", "3 of 3 files hashed"),
    ("OBS-0002-0008", "CHK-0002-0004", "D6", "/data/studio/projects/aurora, size exactly 16384: empty list, truncated false, no unreadable subfolder", "complete to depth 8, limit 200"),
    ("OBS-0002-0009", "CHK-0002-0005", "D6", "/data/studio/backups/aurora-2026-10-01, size exactly 16384: 1 file /data/studio/backups/aurora-2026-10-01/layout.indd 16384 bytes mtime 1200; truncated false, no unreadable subfolder", "complete to depth 8, limit 200"),
    ("OBS-0002-0010", "CHK-0002-0005", "D6", "/data/studio/backups/aurora-2026-11-05, size exactly 16384: empty list, truncated false, no unreadable subfolder", "complete to depth 8, limit 200"),
    ("OBS-0002-0011", "CHK-0002-0005", "D6", "/data/studio/usb-archive/aurora, size exactly 16384: empty list, truncated false, no unreadable subfolder", "complete to depth 8, limit 200"),
    ("OBS-0002-0012", "CHK-0002-0006", "D7", "/data/studio/backups/aurora-2026-10-01/layout.indd sha256 " + V6 + ", 16384 bytes, matches VER-0001-0006", "1 of 1 files hashed"),
]
for o in obs:
    R(o[0], type="observation", check_card=o[1], agent="file-agent", delegation=o[2], state="completed", result=o[3], coverage=o[4], observed_at="unknown", class_="observed")


def CLM(rid, kind, subj, stmt, cls, sup, con, dep, **extra):
    f = dict(type="claim", kind=kind, subject=subj)
    f.update(extra)
    f.update(statement=stmt, class_=cls, supports=sup, contradicts=con, depends_on=dep, status="current")
    R(rid, **f)


CLM("CLM-0002-0001", "asset-state", "AST-0001-0006", "layout.indd is absent at its recorded path /data/studio/projects/aurora/layout.indd and no 16384-byte file exists in the project to depth 8; cause unknown", "observed", ["OBS-0002-0006", "OBS-0002-0008"], [], ["AST-0001-0006", "OBS-0002-0006", "OBS-0002-0008"], asset_state="missing", located_at=None)
CLM("CLM-0002-0002", "asset-state", "AST-0001-0002", "copy.docx at its recorded path matches approved version VER-0001-0002", "observed", ["OBS-0002-0007"], [], ["VER-0001-0002", "OBS-0002-0007"], asset_state="intact", located_at="/data/studio/projects/aurora/copy.docx")
CLM("CLM-0002-0003", "asset-state", "AST-0001-0003", "cover.tif at its recorded path matches approved version VER-0001-0003", "observed", ["OBS-0002-0007"], [], ["VER-0001-0003", "OBS-0002-0007"], asset_state="intact", located_at="/data/studio/projects/aurora/cover.tif")
CLM("CLM-0002-0004", "asset-state", "AST-0001-0007", "logo.ai at its recorded path matches approved version VER-0001-0007", "observed", ["OBS-0002-0007"], [], ["VER-0001-0007", "OBS-0002-0007"], asset_state="intact", located_at="/data/studio/projects/aurora/logo.ai")
ords = [
    ("CLM-0002-0005", "AST-0001-0004", "cover-preview.jpg", "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"),
    ("CLM-0002-0006", "AST-0001-0005", "fonts-license.pdf", "/data/studio/projects/aurora/fonts-license.pdf"),
    ("CLM-0002-0007", "AST-0001-0008", "palette.ase", "/data/studio/projects/aurora/palette.ase"),
    ("CLM-0002-0008", "AST-0001-0009", "DSC_0101.ARW", "/data/studio/projects/aurora/raw/DSC_0101.ARW"),
    ("CLM-0002-0009", "AST-0001-0010", "DSC_0142.ARW", "/data/studio/projects/aurora/raw/DSC_0142.ARW"),
    ("CLM-0002-0010", "AST-0001-0011", "DSC_0150.ARW", "/data/studio/projects/aurora/raw/DSC_0150.ARW"),
]
for rid, a, n, p in ords:
    CLM(rid, "asset-state", a, n + " is present with the recorded size and time; content not hashed in this session", "observed", ["OBS-0002-0006"], [], [a, "OBS-0002-0006"], asset_state="intact-metadata", located_at=p)
CLM("CLM-0002-0011", "asset-state", "AST-0001-0001", "brief.pdf state is unknown: its recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical, so it was not read", "unknown", [], [], ["AST-0001-0001"], asset_state="unknown", located_at=None)
CLM("CLM-0002-0012", "contradiction", "CPY-0001-0006", "copy record CPY-0001-0006 (OBS-0001-0006) records VER-0001-0006 at /data/studio/projects/aurora/layout.indd; D5 in this session reports that path not found", "contradicted", ["OBS-0002-0006"], ["CPY-0001-0006", "OBS-0001-0006"], ["CPY-0001-0006", "OBS-0002-0006"])
CLM("CLM-0002-0013", "copy-eligibility", "CPY-0001-0015", "copy record CPY-0001-0015 names location LOC-0001-0002 (/data/studio/backups/aurora-2026-10-01) but its real path /data/studio/private/other-client/layout.indd is outside that root; excluded and not read", "inferred", [], [], ["CPY-0001-0015", "LOC-0001-0002"])
CLM("CLM-0002-0014", "copy-found", "VER-0001-0006", "/data/studio/backups/aurora-2026-10-01/layout.indd holds VER-0001-0006 (digest equal); it is not among the baseline copy records and its mtime 1200 is later than the scope newest_mtime 1104; its origin is unknown", "observed", ["OBS-0002-0009", "OBS-0002-0012"], [], ["VER-0001-0006", "OBS-0002-0009", "OBS-0002-0012"])

hyps = [
    ("HYP-0002-0001", "layout.indd moved or renamed inside the project", "refuted", [], ["OBS-0002-0008"], "none: project search for 16384-byte files complete to depth 8"),
    ("HYP-0002-0002", "layout.indd absent from the project with a copy of VER-0001-0006 elsewhere", "supported", ["OBS-0002-0009", "OBS-0002-0012"], [], "recover from the verified copy"),
    ("HYP-0002-0003", "layout.indd absent without any copy of VER-0001-0006", "refuted", [], ["OBS-0002-0012"], "none"),
    ("HYP-0002-0004", "layout.indd present but not visible to the NAS", "undetermined", [], ["OBS-0002-0006"], "none available: D5 returned not_found, not a permission error"),
]
for h in hyps:
    R(h[0], type="hypothesis", subject="AST-0001-0006", text=h[1], status=h[2], for_=h[3], against=h[4], next_check=h[5])

opn = [
    ("OPN-0002-0001", "AST-0001-0001", "recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical and points outside the project; brief.pdf was not read and its state is unknown", "the user states the correct path of brief.pdf and a new Baseline records it"),
    ("OPN-0002-0002", "CPY-0001-0015", "copy record real path /data/studio/private/other-client/layout.indd lies outside its location /data/studio/backups/aurora-2026-10-01; excluded and not read", "a new Baseline of the copy locations replaces this record"),
    ("OPN-0002-0003", "AST-0001-0006", "cause of the absence of layout.indd is unknown; no source in this session states it; the project was not fully listed, so new files or notes were not reviewed", "a full listing of the project and a document question, if the user asks what happened"),
    ("OPN-0002-0004", "CPY-0002-0001", "the copy at /data/studio/backups/aurora-2026-10-01/layout.indd is not in the baseline and has mtime 1200; who placed it there is unknown", "a user statement about that backup folder"),
]
for o in opn:
    R(o[0], type="open-item", subject=o[1], reason=o[2], needed_to_resolve=o[3])

R("CPY-0002-0001", type="copy", version_id="VER-0001-0006", real_path="/data/studio/backups/aurora-2026-10-01/layout.indd", location_id="LOC-0001-0002", sha256=V6, observation="OBS-0002-0012", access="readable", status="current")
R("CPY-0002-0002", type="copy", version_id="VER-0001-0006", real_path="/data/studio/projects/aurora/layout.indd", location_id="LOC-0001-0001", sha256=None, observation="OBS-0002-0006", access="unknown", status="needs-review", supersedes="CPY-0001-0006")

R("PLN-0002-01", type="plan", case_id="CAS-0002", revision=1, reference="approved-version", target_set="SET-0001-0002",
  recovery_folder=RF,
  goal="Recover approved set SET-0001-0002 (Delivery 2; record file /data/studio/cerbero-memory/CERBERO-B-0001-01.md; approving statements STM-0001-0005 and STM-0001-0003) member layout.indd (AST-0001-0006) at version VER-0001-0006. Members copy.docx (VER-0001-0002), cover.tif (VER-0001-0003) and logo.ai (VER-0001-0007) are intact at their recorded paths and are not copied. Member brief.pdf (AST-0001-0001, VER-0001-0001) is unknown and stays pending. Operations: create the new folder " + RF + " with no subfolders; copy, never move and never overwrite, entry ENT-0002-01-01.",
  preconditions="The user confirmed this plan ID, its saved digest and the target set SET-0001-0002 in this session. The saved plan file digest, observed again immediately before the first change, equals the confirmed digest. mkdir and cpmv in copy mode without overwrite are in the capability evidence and the expert reports them allowed. The NAS approval of each change is answered by the user. Per entry: the source real path lies inside /data/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals the expected digest; the destination does not exist and lies inside the recovery folder.",
  success_conditions="The recovery folder exists at the planned real path returned by the NAS. Per entry: the destination exists at the planned real path returned by the NAS and its digest equals the expected digest.",
  risks="The source may change between the check and the copy; no atomic copy; the copy in /data/studio/backups/aurora-2026-10-01 is not in the baseline and its origin is unknown (OPN-0002-0004); digests and memory are on the same NAS and are not an independent root of trust; brief.pdf is unknown, so this plan cannot show the Delivery 2 set complete.",
  pending=["AST-0001-0001 brief.pdf: state unknown, recorded path not canonical (OPN-0002-0001)"],
  previous_receipt=None, supersedes_plan=None)
R("ENT-0002-01-01", type="plan-entry", plan_id="PLN-0002-01", asset_id="AST-0001-0006", name="layout.indd", version_id="VER-0001-0006", expected_sha256=V6, size_bytes=16384, source_path="/data/studio/backups/aurora-2026-10-01/layout.indd", destination_path=RF + "/layout.indd")
