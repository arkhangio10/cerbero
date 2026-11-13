# CERBERO BUNDLE B-0002-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-01"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0002
- type: "case"
- scope_id: "SCP-0001"
- request: "layout.indd is missing from project Aurora. Recover the Delivery 2 version."
- status: "open"
- opened_in: "this session"

## RECORD STM-0002-0001
- type: "statement"
- text: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /volume1/studio/projects/aurora. Cerbero memory folder: /volume1/studio/cerbero-memory. Copy locations: /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora. Create the recovery folder under /volume1/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD OBS-0002-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D1"
- state: "completed"
- result: "current user folder real path: /volume1/studio"
- coverage: "1 query"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "exists, readable, real path equal to the given path: /volume1/studio/projects/aurora, /volume1/studio/cerbero-memory, /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05, /volume1/studio/usb-archive/aurora, /volume1/studio/recovered. /volume1/studio: exists false, reason not found"
- coverage: "7 folders queried"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "/volume1/studio/cerbero-memory/CERBERO-B-0001-01.md 20963 bytes modified 3001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md 383 bytes modified 3002"
- coverage: "2 entries, limit 200, truncated false"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D4"
- state: "completed"
- result: "full text returned for CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md; no file reported missing, unreadable or partial; both parse as cerbero-memory-2; no policy, plan or receipt records"
- coverage: "2 of 2 files read"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0001
- type: "check-card"
- doubt: "Does CERBERO-B-0001-01.md still match the digest listed in IDX-0001-01?"
- decision: "whether approved set SET-0001-0002, its versions and its copies can be used as evidence"
- operation: "D7 file-agent"
- outcomes: "equal: records usable; different: file needs-review and no baseline evidence"
- cost: "2 digests, about 21 KB, read-only"
- budget_left: 300

## RECORD OBS-0002-0005
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 0589d203a592b05653d6b2c36b37879bd62506966497a4ecc54c887061744c0d 20963 bytes, matches IDX-0001-01-0001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md sha256 d48d2e2b404273c949663bc149a568d1f42a680b6c73f73cf1576fa37bfbf41b 383 bytes"
- coverage: "2 of 2 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Which recorded assets of SCP-0001 are still at their recorded paths with the recorded size and modification time?"
- decision: "which assets need a digest and which need the missing-asset search"
- operation: "D5 file-agent"
- outcomes: "present and equal: digest for critical assets, intact-metadata for ordinary ones; changed: digest; missing: D6 exact-size search"
- cost: "metadata of 11 paths, read-only"
- budget_left: 298

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "10 of 11 recorded paths exist, readable, real path equal to the recorded path, size and modification time equal to the asset records (brief.pdf 4096/1100, copy.docx 6144/1102, cover.tif 32768/1103, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, logo.ai 8192/900, palette.ase 512/900, raw/DSC_0101.ARW 65536/800, raw/DSC_0142.ARW 65536/801, raw/DSC_0150.ARW 65536/802); /volume1/studio/projects/aurora/layout.indd exists false, reason not_found"
- coverage: "11 of 11 asset records checked by metadata"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Are brief.pdf, copy.docx, cover.tif and logo.ai still the Delivery 2 versions?"
- decision: "whether these members need recovery"
- operation: "D7 file-agent"
- outcomes: "digest equal to VER-0001-0001, VER-0001-0002, VER-0001-0003, VER-0001-0007: intact; different: altered, recover"
- cost: "4 digests, 51200 bytes, read-only"
- budget_left: 298

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/projects/aurora/brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 bytes matches; /volume1/studio/projects/aurora/copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes matches; /volume1/studio/projects/aurora/cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes matches; /volume1/studio/projects/aurora/logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes matches"
- coverage: "4 of 4 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Is a file of exactly 16384 bytes, the size of VER-0001-0006, anywhere else in the project folder?"
- decision: "whether layout.indd is moved inside the scope or missing"
- operation: "D6 file-agent"
- outcomes: "candidates: D7 against VER-0001-0006; empty and complete: moved-in-scope refuted; possibly incomplete: D13 split"
- cost: "1 size-filtered listing, read-only"
- budget_left: 294

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "under /volume1/studio/projects/aurora, regular files whose size is exactly 16384 bytes: empty list"
- coverage: "0 entries, limit 200, depth 8, truncated false, no unreadable subfolder: complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Does recorded copy CPY-0001-0015 still exist at its recorded path inside the real root of LOC-0001-0002?"
- decision: "whether it can be the recovery source for VER-0001-0006"
- operation: "D5 file-agent"
- outcomes: "present inside the root with 16384 bytes: D7; missing or outside: search the other named locations"
- cost: "metadata of 1 path, read-only"
- budget_left: 294

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "/volume1/studio/backups/aurora-2026-10-01/layout.indd exists, readable, real path equal to the given path, 16384 bytes, modified 1200"
- coverage: "1 of 1 paths checked"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0006
- type: "check-card"
- doubt: "Is /volume1/studio/backups/aurora-2026-10-01/layout.indd still version VER-0001-0006?"
- decision: "whether the recovery plan has a backed source"
- operation: "D7 file-agent"
- outcomes: "equal: eligible source, verified-now; different: contradiction, CPY-0001-0015 needs-review, search the other named locations"
- cost: "1 digest, 16384 bytes, read-only"
- budget_left: 294

## RECORD OBS-0002-0010
- type: "observation"
- check_card: "CHK-0002-0006"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b 16384 bytes, matches VER-0001-0006"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0002-0001
- type: "claim"
- kind: "contradiction"
- subject: "/volume1/studio"
- statement: "D1 reports /volume1/studio as the real path of the current user folder; D2 reports /volume1/studio as not found. Nothing in this case depends on it: it is not an authorized root."
- class: "contradicted"
- supports: ["OBS-0002-0001"]
- contradicts: ["OBS-0002-0002"]
- depends_on: ["OBS-0002-0001", "OBS-0002-0002"]
- status: "current"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "Copy record CPY-0001-0006 places VER-0001-0006 at /volume1/studio/projects/aurora/layout.indd; D5 in this session reports that path not_found."
- class: "contradicted"
- supports: ["OBS-0002-0006"]
- contradicts: ["CPY-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0002-0006"]
- status: "current"

## RECORD CPY-0002-0001
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/volume1/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "layout.indd is absent at its recorded path; no file of 16384 bytes exists in the project folder to depth 8. Cause unknown."
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0008"]
- contradicts: []
- depends_on: ["AST-0001-0006", "VER-0001-0006", "OBS-0002-0006", "OBS-0002-0008"]
- status: "current"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/brief.pdf"
- statement: "brief.pdf at its recorded path matches approved version VER-0001-0001"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0001", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/copy.docx"
- statement: "copy.docx at its recorded path matches approved version VER-0001-0002"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/cover.tif"
- statement: "cover.tif at its recorded path matches approved version VER-0001-0003"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0003", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/logo.ai"
- statement: "logo.ai at its recorded path matches approved version VER-0001-0007"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/exports/previews/cover-preview.jpg"
- statement: "cover-preview.jpg has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0004", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/fonts-license.pdf"
- statement: "fonts-license.pdf has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0005", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/palette.ase"
- statement: "palette.ase has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0008", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/raw/DSC_0101.ARW"
- statement: "raw/DSC_0101.ARW has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0009", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0012
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/raw/DSC_0142.ARW"
- statement: "raw/DSC_0142.ARW has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0010", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0013
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/raw/DSC_0150.ARW"
- statement: "raw/DSC_0150.ARW has the recorded size and modification time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["AST-0001-0011", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0014
- type: "claim"
- kind: "copy-check"
- subject: "CPY-0001-0015"
- statement: "/volume1/studio/backups/aurora-2026-10-01/layout.indd is inside the real root of LOC-0001-0002 and its digest re-observed in this session equals VER-0001-0006: eligible, verified-now"
- class: "observed"
- supports: ["OBS-0002-0009", "OBS-0002-0010"]
- contradicts: []
- depends_on: ["CPY-0001-0015", "VER-0001-0006", "OBS-0002-0009", "OBS-0002-0010"]
- status: "current"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd was moved or renamed inside the project folder with its content unchanged"
- status: "refuted"
- for: []
- against: ["OBS-0002-0008"]
- next_check: "none; the size search was complete to depth 8 only"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent from the project and a copy of VER-0001-0006 exists in a named location"
- status: "supported"
- for: ["OBS-0002-0009", "OBS-0002-0010"]
- against: []
- next_check: "none"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent and no copy of VER-0001-0006 exists"
- status: "refuted"
- for: []
- against: ["OBS-0002-0010"]
- next_check: "none"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is present in the project but not visible to the NAS listing"
- status: "undetermined"
- for: []
- against: ["OBS-0002-0006", "OBS-0002-0008"]
- next_check: "none available within the capability evidence of this Skill"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "AST-0001-0006"
- reason: "the cause of the absence of layout.indd is unknown: no source states it"
- needed_to_resolve: "a user statement or a project document that states the cause"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "/volume1/studio"
- reason: "D1 and D2 disagree on whether /volume1/studio exists"
- needed_to_resolve: "nothing in this case depends on it; a later check if the user folder becomes relevant"

## RECORD OPN-0002-0003
- type: "open-item"
- subject: "VER-0001-0006"
- reason: "/volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora were not searched in this session for other copies of VER-0001-0006; the baseline recorded none there"
- needed_to_resolve: "D6 and D7 in those locations, only if another source is ever needed"

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/volume1/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "Recover approved set SET-0001-0002 (Delivery 2) member layout.indd, version VER-0001-0006 (sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes), the only member missing or altered. Members brief.pdf (VER-0001-0001), copy.docx (VER-0001-0002), cover.tif (VER-0001-0003) and logo.ai (VER-0001-0007) are intact in the project and are not copied. Target set record file: /volume1/studio/cerbero-memory/CERBERO-B-0001-01.md; approving statement STM-0001-0005."
- preconditions: "The user confirms this plan ID, its saved digest and approved set SET-0001-0002 (Delivery 2). The saved plan file is hashed again immediately before the first change and equals the confirmed digest. The NAS approval for each change is requested from and answered by the user. Operations: create the new folder /volume1/studio/recovered/cerbero-recovery-CAS-0002 with no subfolders; copy each source to its destination, never move, never overwrite. Per entry: the source real path lies inside /volume1/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals the expected digest; the destination does not exist and lies inside the recovery folder."
- success_conditions: "Per entry: the destination exists at the planned real path returned by the NAS, and its digest equals the expected digest."
- risks: "The source may change between its check and the copy; the copy is not atomic; the project, the copies, the memory folder and the recovery folder are on the same NAS, so these digests are not an independent root of trust; the cause of the absence is unknown; the recovered file goes to the recovery folder and nothing is placed back at the original path."
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
- source_path: "/volume1/studio/backups/aurora-2026-10-01/layout.indd"
- destination_path: "/volume1/studio/recovered/cerbero-recovery-CAS-0002/layout.indd"
