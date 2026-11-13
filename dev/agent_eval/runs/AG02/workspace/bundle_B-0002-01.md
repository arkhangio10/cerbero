# CERBERO BUNDLE B-0002-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-01"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0002
- type: "case"
- scope_id: "SCP-0001"
- request: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."
- status: "open"
- opened_in: "this session"

## RECORD STM-0002-0001
- type: "statement"
- text: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD CHK-0002-0001
- type: "check-card"
- doubt: "Does CERBERO-B-0001-01.md still match its index digest 6828..2259 (IDX-0001-01-0001)?"
- decision: "whether the baseline records (SET-0001-0002, versions, copies) can be used as evidence"
- operation: "D7 file-agent, plus the digest of CERBERO-IDX-0001-01.md for the end-of-session index"
- outcomes: "match: records usable; differs: needs-review, no approved reference"
- cost: "2 digests, about 21 KB, read-only"
- budget_left: 300

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Are the 11 recorded assets of SCP-0001 present at their recorded paths with the recorded size and modification time?"
- decision: "which assets need digest checks and which are missing and need search or recovery"
- operation: "D5 file-agent on the 11 recorded paths, all canonical and inside /data/studio/projects/aurora"
- outcomes: "absent: test moved, copy elsewhere, no copy, not visible; present with equal metadata: D7 for critical assets; different metadata: D7"
- cost: "metadata only, read-only"
- budget_left: 298

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Was layout.indd (VER-0001-0006, 16384 bytes) moved or renamed inside the project?"
- decision: "moved inside scope: report the new path and do not copy; not found: recover from a copy"
- operation: "D6 file-agent, search_root /data/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D7 against 84a4..1e1b; empty and complete: moved inside scope refuted to depth 8; possibly incomplete: split with D13"
- cost: "1 size-filtered listing, read-only"
- budget_left: 298

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Does the recorded copy CPY-0001-0015 (/data/studio/backups/aurora-2026-10-01/layout.indd) still exist inside its location root?"
- decision: "whether it can be the recovery source of layout.indd"
- operation: "D5 file-agent on a path from memory, canonical and inside the LOC-0001-0002 root"
- outcomes: "present inside the root with 16384 bytes: D7; absent or outside: next candidate, then search the other named locations"
- cost: "metadata only, read-only"
- budget_left: 298

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Are brief.pdf, copy.docx, cover.tif and logo.ai still their Delivery 2 versions, and is the backup copy of layout.indd still VER-0001-0006?"
- decision: "which set members need recovery, and whether CPY-0001-0015 is a valid source"
- operation: "D7 file-agent on 5 files with expected digests"
- outcomes: "match: intact or eligible source; differs: altered or candidate rejected, search the other named locations"
- cost: "5 digests, about 67.6 KB, read-only"
- budget_left: 298

## RECORD OBS-0002-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D1"
- state: "completed"
- result: "user folder real path /data/studio"
- coverage: "1 of 1"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "7 of 7 folders exist and are readable, real path equal to the given path: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio"
- coverage: "7 of 7"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "2 files: /data/studio/cerbero-memory/CERBERO-B-0001-01.md 20942 bytes mtime 3001; /data/studio/cerbero-memory/CERBERO-IDX-0001-01.md 380 bytes mtime 3002"
- coverage: "2 entries, truncated false"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D4"
- state: "completed"
- result: "2 files returned in full: CERBERO-IDX-0001-01.md, CERBERO-B-0001-01.md"
- coverage: "2 of 2, none reported partial"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0005
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 682855fb8e2e81be54754163486d42504ac98e272ed3d002cef9a7ae8cd62259 20942 bytes, matches index entry IDX-0001-01-0001; /data/studio/cerbero-memory/CERBERO-IDX-0001-01.md sha256 4cf8bbe0ec55f7ec826eb8c5ceba33f042467747e2c07d7b88ba977f86ec7e0b 380 bytes"
- coverage: "2 of 2 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "10 of 11 recorded asset paths exist, readable, real path equal to the recorded path, size and mtime equal to the recorded values (brief.pdf 4096/1100, copy.docx 6144/1102, cover.tif 32768/1103, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, logo.ai 8192/900, palette.ase 512/900, raw/DSC_0101.ARW 65536/800, raw/DSC_0142.ARW 65536/801, raw/DSC_0150.ARW 65536/802); /data/studio/projects/aurora/layout.indd exists false, reason not_found"
- coverage: "11 of 11 paths checked by metadata"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "under /data/studio/projects/aurora, depth 8, regular files of exactly 16384 bytes: 0 files, truncated false, no unreadable subfolders"
- coverage: "complete to depth 8: 0 entries of limit 200, truncation reported absent, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-10-01/layout.indd exists, readable, real path /data/studio/backups/aurora-2026-10-01/layout.indd, 16384 bytes, mtime 1200"
- coverage: "1 of 1"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-10-01/layout.indd 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b 16384 bytes matches VER-0001-0006; /data/studio/projects/aurora/brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 bytes matches VER-0001-0001; /data/studio/projects/aurora/copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes matches VER-0001-0002; /data/studio/projects/aurora/cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes matches VER-0001-0003; /data/studio/projects/aurora/logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes matches VER-0001-0007"
- coverage: "5 of 5 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0002-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "layout.indd is absent at /data/studio/projects/aurora/layout.indd; no file of 16384 bytes exists in the project to depth 8 (search complete); cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["AST-0001-0006", "VER-0001-0006", "/data/studio/projects/aurora/layout.indd absent (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/brief.pdf"
- statement: "brief.pdf at its recorded path has the digest of Delivery 2 version VER-0001-0001"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["AST-0001-0001", "VER-0001-0001", "/data/studio/projects/aurora/brief.pdf sha256 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"]
- status: "current"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/copy.docx"
- statement: "copy.docx at its recorded path has the digest of Delivery 2 version VER-0001-0002"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["AST-0001-0002", "VER-0001-0002", "/data/studio/projects/aurora/copy.docx sha256 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"]
- status: "current"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/cover.tif"
- statement: "cover.tif at its recorded path has the digest of Delivery 2 version VER-0001-0003"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["AST-0001-0003", "VER-0001-0003", "/data/studio/projects/aurora/cover.tif sha256 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"]
- status: "current"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/logo.ai"
- statement: "logo.ai at its recorded path has the digest of Delivery 2 version VER-0001-0007"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["AST-0001-0007", "VER-0001-0007", "/data/studio/projects/aurora/logo.ai sha256 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"]
- status: "current"

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"
- statement: "exports/previews/cover-preview.jpg present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0004", "/data/studio/projects/aurora/exports/previews/cover-preview.jpg metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/fonts-license.pdf"
- statement: "fonts-license.pdf present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0005", "/data/studio/projects/aurora/fonts-license.pdf metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/palette.ase"
- statement: "palette.ase present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0008", "/data/studio/projects/aurora/palette.ase metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0101.ARW"
- statement: "raw/DSC_0101.ARW present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0009", "/data/studio/projects/aurora/raw/DSC_0101.ARW metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- statement: "raw/DSC_0142.ARW present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0010", "/data/studio/projects/aurora/raw/DSC_0142.ARW metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0150.ARW"
- statement: "raw/DSC_0150.ARW present with recorded size and mtime; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0011", "/data/studio/projects/aurora/raw/DSC_0150.ARW metadata (OBS-0002-0006)"]
- status: "current"

## RECORD CLM-0002-0012
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "copy record CPY-0001-0006 (OBS-0001-0006) places VER-0001-0006 at /data/studio/projects/aurora/layout.indd; D5 in this session reports that path not_found (OBS-0002-0006)"
- class: "contradicted"
- supports: ["OBS-0002-0006"]
- contradicts: ["CPY-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0002-0006"]
- status: "current"

## RECORD CPY-0002-0001
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD CLM-0002-0013
- type: "claim"
- kind: "copy-verification"
- subject: "CPY-0001-0015"
- statement: "copy CPY-0001-0015 at /data/studio/backups/aurora-2026-10-01/layout.indd re-observed in this session with the digest of VER-0001-0006 (evidence level verified-now); its 16384-byte size and real path inside LOC-0001-0002 were confirmed first"
- class: "observed"
- supports: ["OBS-0002-0008", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["CPY-0001-0015", "VER-0001-0006", "/data/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"]
- status: "current"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd was moved or renamed inside the project with unchanged content"
- status: "refuted"
- for: []
- against: ["OBS-0002-0007"]
- next_check: "none: exact-size search complete to depth 8"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent from the project and a copy of VER-0001-0006 exists in a named location"
- status: "supported"
- for: ["OBS-0002-0006", "OBS-0002-0007", "OBS-0002-0009"]
- against: []
- next_check: "none"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent and no copy of VER-0001-0006 exists"
- status: "refuted"
- for: []
- against: ["OBS-0002-0009"]
- next_check: "none"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is present but not visible to this account"
- status: "undetermined"
- for: []
- against: ["OBS-0002-0006", "OBS-0002-0007"]
- next_check: "none available in the capability evidence: D5 reported not_found rather than unreadable and D6 named no unreadable subfolder"

## RECORD HYP-0002-0005
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "an edited version of layout.indd with a different size exists under another name in the project"
- status: "open"
- for: []
- against: []
- next_check: "one D6 listing of the project of any size; not run because the user did not ask what happened and its result would not change the recovery of VER-0001-0006"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "AST-0001-0006"
- reason: "cause of the disappearance of layout.indd is unknown; no source states it"
- needed_to_resolve: "a user statement or a cited project document that states it"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "SCP-0001"
- reason: "the project folder was not listed in full in this session; new or renamed files of other sizes were not reviewed"
- needed_to_resolve: "one D6 listing of /data/studio/projects/aurora of any size"

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/data/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "Recover approved set SET-0001-0002 (Delivery 2) member layout.indd, version VER-0001-0006 (sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes), into the new folder /data/studio/recovered/cerbero-recovery-CAS-0002. Target set members: brief.pdf VER-0001-0001, layout.indd VER-0001-0006, copy.docx VER-0001-0002, cover.tif VER-0001-0003, logo.ai VER-0001-0007; record file /data/studio/cerbero-memory/CERBERO-B-0001-01.md; approving statement STM-0001-0005. The other four members were observed intact in this session (CLM-0002-0002 to CLM-0002-0005) and are not copied. Operations: create /data/studio/recovered/cerbero-recovery-CAS-0002 with no subfolders; copy, never move, never overwrite, /data/studio/backups/aurora-2026-10-01/layout.indd to /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd."
- preconditions: "The user confirmed plan PLN-0002-01, its saved digest and target set SET-0001-0002 in this session; mkdir and cpmv in copy mode without overwrite are in the capability evidence and the expert reports them allowed; the saved plan file, hashed again immediately before the first change, has the confirmed digest; the source real path lies inside /data/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b; the destination does not exist and lies inside /data/studio/recovered/cerbero-recovery-CAS-0002; the NAS approval of the folder and of the copy is answered by the user."
- success_conditions: "The folder exists at the real path /data/studio/recovered/cerbero-recovery-CAS-0002 returned by the NAS; the copy exists at the planned real path /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd returned by the NAS; its digest equals 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b."
- risks: "Single eligible source (CPY-0001-0015), on Volume 2 of this NAS per STM-0001-0003; the source may change before or during the copy (it is hashed before, and again if the destination differs); the copy is not atomic; memory, copies and digests are on the same NAS and are not an independent root of trust; the cause of the disappearance is unknown (OPN-0002-0001); the project was not listed in full (OPN-0002-0002)."
- pending: []
- previous_receipt: null
- supersedes_plan: null

## RECORD ENT-0002-01-01
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0006"
- name: "layout.indd"
- version_id: "VER-0001-0006"
- expected_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- size_bytes: 16384
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd"
