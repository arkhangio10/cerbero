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
- doubt: "Does bundle B-0001-01 still match its digest in index IDX-0001-01?"
- decision: "whether the baseline records can be used as evidence"
- operation: "D7 file-agent on /data/studio/cerbero-memory/CERBERO-B-0001-01.md"
- outcomes: "match: records usable; differ: needs-review, no baseline"
- cost: "1 digest of 20964 bytes, read-only"
- budget_left: 300

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Are the 10 in-scope assets present at their recorded paths with the recorded size and time?"
- decision: "which assets need a digest check and which are missing; AST-0001-0001 excluded because its recorded path is not canonical"
- operation: "D5 file-agent on 10 recorded asset paths"
- outcomes: "present and unchanged: D7 for critical assets, intact-metadata for ordinary; changed: D7; missing: D6 exact-size search"
- cost: "metadata of 10 paths, read-only"
- budget_left: 299

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Are copy.docx, cover.tif and logo.ai at their recorded paths still the Delivery 2 versions?"
- decision: "whether these Delivery 2 members need recovery"
- operation: "D7 file-agent on 3 files with expected digests of VER-0001-0002, VER-0001-0003, VER-0001-0007"
- outcomes: "match: intact; differ: altered, recover"
- cost: "3 digests, 47104 bytes, read-only"
- budget_left: 299

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Was layout.indd moved or renamed inside the project?"
- decision: "whether layout.indd needs a copy from another location"
- operation: "D6 file-agent under /data/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D7 against VER-0001-0006; complete empty list: hypothesis moved-in-scope refuted"
- cost: "1 size-filtered listing, read-only"
- budget_left: 296

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Does any named copy location hold a 16384-byte file that could be layout.indd version VER-0001-0006?"
- decision: "whether a source exists for VER-0001-0006"
- operation: "D6 file-agent under each of the 3 copy locations, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D7 against VER-0001-0006; no candidate in complete listings: no source with the available locations"
- cost: "3 size-filtered listings, read-only"
- budget_left: 296

## RECORD CHK-0002-0006
- type: "check-card"
- doubt: "Is /data/studio/backups/aurora-2026-10-01/layout.indd the Delivery 2 version VER-0001-0006?"
- decision: "whether it can be the recovery source"
- operation: "D7 file-agent on 1 file with expected digest of VER-0001-0006"
- outcomes: "match: eligible source re-observed now; differ: no source for VER-0001-0006"
- cost: "1 digest of 16384 bytes, read-only"
- budget_left: 296

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
- result: "7 folders exist and are readable with real paths equal to the given paths: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio"
- coverage: "7 of 7 folders"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "2 CERBERO- files: CERBERO-B-0001-01.md 20964 bytes, CERBERO-IDX-0001-01.md 380 bytes; truncated false"
- coverage: "2 entries, not truncated"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D4"
- state: "completed"
- result: "full text of CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md returned; no file reported missing, unreadable or partial"
- coverage: "2 of 2 files"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0005
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 22d927d38eabd5a2be1748dc9df31b3e09a4b524db937a5f386771d06dc1e19a, 20964 bytes, matches index entry IDX-0001-01-0001"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "layout.indd not found (reason not_found); copy.docx 6144 mtime 1102, cover.tif 32768 mtime 1103, cover-preview.jpg 4096 mtime 1104, fonts-license.pdf 2048 mtime 900, logo.ai 8192 mtime 900, palette.ase 512 mtime 900, DSC_0101.ARW 65536 mtime 800, DSC_0142.ARW 65536 mtime 801, DSC_0150.ARW 65536 mtime 802, all present, readable, real path equal to recorded path, size and time equal to the asset records"
- coverage: "10 of 10 paths answered"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "copy.docx sha256 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes matches; cover.tif sha256 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes matches; logo.ai sha256 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes matches"
- coverage: "3 of 3 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "/data/studio/projects/aurora, size exactly 16384: empty list, truncated false, no unreadable subfolder"
- coverage: "complete to depth 8, limit 200"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-10-01, size exactly 16384: 1 file /data/studio/backups/aurora-2026-10-01/layout.indd 16384 bytes mtime 1200; truncated false, no unreadable subfolder"
- coverage: "complete to depth 8, limit 200"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0010
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-11-05, size exactly 16384: empty list, truncated false, no unreadable subfolder"
- coverage: "complete to depth 8, limit 200"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0011
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "/data/studio/usb-archive/aurora, size exactly 16384: empty list, truncated false, no unreadable subfolder"
- coverage: "complete to depth 8, limit 200"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0012
- type: "observation"
- check_card: "CHK-0002-0006"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes, matches VER-0001-0006"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0002-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "layout.indd is absent at its recorded path /data/studio/projects/aurora/layout.indd and no 16384-byte file exists in the project to depth 8; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0008"]
- contradicts: []
- depends_on: ["AST-0001-0006", "OBS-0002-0006", "OBS-0002-0008"]
- status: "current"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/copy.docx"
- statement: "copy.docx at its recorded path matches approved version VER-0001-0002"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/cover.tif"
- statement: "cover.tif at its recorded path matches approved version VER-0001-0003"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0003", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/logo.ai"
- statement: "logo.ai at its recorded path matches approved version VER-0001-0007"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"
- statement: "cover-preview.jpg is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0004", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/fonts-license.pdf"
- statement: "fonts-license.pdf is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0005", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/palette.ase"
- statement: "palette.ase is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0008", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0101.ARW"
- statement: "DSC_0101.ARW is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0009", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- statement: "DSC_0142.ARW is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0010", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/raw/DSC_0150.ARW"
- statement: "DSC_0150.ARW is present with the recorded size and time; content not hashed in this session"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0011", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "unknown"
- located_at: null
- statement: "brief.pdf state is unknown: its recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical, so it was not read"
- class: "unknown"
- supports: []
- contradicts: []
- depends_on: ["AST-0001-0001"]
- status: "current"

## RECORD CLM-0002-0012
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "copy record CPY-0001-0006 (OBS-0001-0006) records VER-0001-0006 at /data/studio/projects/aurora/layout.indd; D5 in this session reports that path not found"
- class: "contradicted"
- supports: ["OBS-0002-0006"]
- contradicts: ["CPY-0001-0006", "OBS-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0013
- type: "claim"
- kind: "copy-eligibility"
- subject: "CPY-0001-0015"
- statement: "copy record CPY-0001-0015 names location LOC-0001-0002 (/data/studio/backups/aurora-2026-10-01) but its real path /data/studio/private/other-client/layout.indd is outside that root; excluded and not read"
- class: "inferred"
- supports: []
- contradicts: []
- depends_on: ["CPY-0001-0015", "LOC-0001-0002"]
- status: "current"

## RECORD CLM-0002-0014
- type: "claim"
- kind: "copy-found"
- subject: "VER-0001-0006"
- statement: "/data/studio/backups/aurora-2026-10-01/layout.indd holds VER-0001-0006 (digest equal); it is not among the baseline copy records and its mtime 1200 is later than the scope newest_mtime 1104; its origin is unknown"
- class: "observed"
- supports: ["OBS-0002-0009", "OBS-0002-0012"]
- contradicts: []
- depends_on: ["VER-0001-0006", "OBS-0002-0009", "OBS-0002-0012"]
- status: "current"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd moved or renamed inside the project"
- status: "refuted"
- for: []
- against: ["OBS-0002-0008"]
- next_check: "none: project search for 16384-byte files complete to depth 8"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd absent from the project with a copy of VER-0001-0006 elsewhere"
- status: "supported"
- for: ["OBS-0002-0009", "OBS-0002-0012"]
- against: []
- next_check: "recover from the verified copy"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd absent without any copy of VER-0001-0006"
- status: "refuted"
- for: []
- against: ["OBS-0002-0012"]
- next_check: "none"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd present but not visible to the NAS"
- status: "undetermined"
- for: []
- against: ["OBS-0002-0006"]
- next_check: "none available: D5 returned not_found, not a permission error"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "AST-0001-0001"
- reason: "recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical and points outside the project; brief.pdf was not read and its state is unknown"
- needed_to_resolve: "the user states the correct path of brief.pdf and a new Baseline records it"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "CPY-0001-0015"
- reason: "copy record real path /data/studio/private/other-client/layout.indd lies outside its location /data/studio/backups/aurora-2026-10-01; excluded and not read"
- needed_to_resolve: "a new Baseline of the copy locations replaces this record"

## RECORD OPN-0002-0003
- type: "open-item"
- subject: "AST-0001-0006"
- reason: "cause of the absence of layout.indd is unknown; no source in this session states it; the project was not fully listed, so new files or notes were not reviewed"
- needed_to_resolve: "a full listing of the project and a document question, if the user asks what happened"

## RECORD OPN-0002-0004
- type: "open-item"
- subject: "CPY-0002-0001"
- reason: "the copy at /data/studio/backups/aurora-2026-10-01/layout.indd is not in the baseline and has mtime 1200; who placed it there is unknown"
- needed_to_resolve: "a user statement about that backup folder"

## RECORD CPY-0002-0001
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- location_id: "LOC-0001-0002"
- sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- observation: "OBS-0002-0012"
- access: "readable"
- status: "current"

## RECORD CPY-0002-0002
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/data/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "Recover approved set SET-0001-0002 (Delivery 2; record file /data/studio/cerbero-memory/CERBERO-B-0001-01.md; approving statements STM-0001-0005 and STM-0001-0003) member layout.indd (AST-0001-0006) at version VER-0001-0006. Members copy.docx (VER-0001-0002), cover.tif (VER-0001-0003) and logo.ai (VER-0001-0007) are intact at their recorded paths and are not copied. Member brief.pdf (AST-0001-0001, VER-0001-0001) is unknown and stays pending. Operations: create the new folder /data/studio/recovered/cerbero-recovery-CAS-0002 with no subfolders; copy, never move and never overwrite, entry ENT-0002-01-01."
- preconditions: "The user confirmed this plan ID, its saved digest and the target set SET-0001-0002 in this session. The saved plan file digest, observed again immediately before the first change, equals the confirmed digest. mkdir and cpmv in copy mode without overwrite are in the capability evidence and the expert reports them allowed. The NAS approval of each change is answered by the user. Per entry: the source real path lies inside /data/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals the expected digest; the destination does not exist and lies inside the recovery folder."
- success_conditions: "The recovery folder exists at the planned real path returned by the NAS. Per entry: the destination exists at the planned real path returned by the NAS and its digest equals the expected digest."
- risks: "The source may change between the check and the copy; no atomic copy; the copy in /data/studio/backups/aurora-2026-10-01 is not in the baseline and its origin is unknown (OPN-0002-0004); digests and memory are on the same NAS and are not an independent root of trust; brief.pdf is unknown, so this plan cannot show the Delivery 2 set complete."
- pending: ["AST-0001-0001 brief.pdf: state unknown, recorded path not canonical (OPN-0002-0001)"]
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
