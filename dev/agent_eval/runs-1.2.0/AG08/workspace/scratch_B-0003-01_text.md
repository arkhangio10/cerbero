# CERBERO BUNDLE B-0003-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0003-01"
- case_id: "CAS-0003"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0003
- type: "case"
- scope_id: "SCP-0001"
- request: "rebuild"
- status: "open"
- opened_in: "this session"

## RECORD STM-0003-0001
- type: "statement"
- text: "Rebuild Delivery 2 of project Aurora in a new folder: all its files, also the ones that are still fine, and tell me where each file came from and what you could check. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the new folder under /data/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD OBS-0003-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "all 7 named folders and the user folder exist, readable, real path equal to the name"
- coverage: "7 of 7 folders"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3 D4 D7"
- state: "completed"
- result: "7 files listed, not truncated; newest index IDX-0002-01; 5 bundles read whole, equal to the index; CERBERO-B-0002-02.md sha256 6e49138c3ebde1506a6b49ed5e7a9d6c323727514dbc7801dcaeee40a721e121"
- coverage: "5 of 5 bundles hashed; IDX-0001-01 superseded, not read"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0001
- type: "check-card"
- doubt: "Are the 11 assets, and brief-FINAL.pdf (CLM-0002-0008), present?"
- decision: "source of each Delivery 2 member"
- operation: "D5 file-agent, 12 paths"
- outcomes: "absent: size search; set member: digest; ordinary unchanged: intact-metadata"
- cost: "metadata, read-only"
- budget_left: 300

## RECORD OBS-0003-0003
- type: "observation"
- check_card: "CHK-0003-0001"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "not_found: brief.pdf, copy.docx, layout.indd, raw/DSC_0142.ARW; the other 7 assets present with recorded size and mtime; brief-FINAL.pdf 736 bytes, mtime 1100; every real path equal to the path asked"
- coverage: "12 of 12 paths"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0002
- type: "check-card"
- doubt: "Do brief-FINAL.pdf, cover.tif, logo.ai hold their Delivery 2 versions?"
- decision: "rebuild source of each present member"
- operation: "D7 file-agent, 3 files"
- outcomes: "equal: source in project; differs: altered"
- cost: "digest of 18324 bytes"
- budget_left: 300

## RECORD OBS-0003-0004
- type: "observation"
- check_card: "CHK-0003-0002"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "brief-FINAL.pdf equal to VER-0001-0001; logo.ai equal to VER-0001-0007; cover.tif d85d08c3852b35a6fdbd2523446c8cf8c2c467c6f985f44890561760dbc75e59, differs from VER-0001-0003"
- coverage: "3 of 3 hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0003
- type: "check-card"
- doubt: "Was copy.docx (968 bytes) moved inside the project?"
- decision: "whether copy.docx must come from a backup"
- operation: "D6 file-agent, size 968, depth 8"
- outcomes: "candidate: hash; empty: missing"
- cost: "size-filtered listing"
- budget_left: 297

## RECORD OBS-0003-0005
- type: "observation"
- check_card: "CHK-0003-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty, not truncated, no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0004
- type: "check-card"
- doubt: "Was layout.indd (16384 bytes) moved inside the project?"
- decision: "whether layout.indd must come from a backup"
- operation: "D6 file-agent, size 16384, depth 8"
- outcomes: "candidate: hash; empty: missing"
- cost: "size-filtered listing"
- budget_left: 297

## RECORD OBS-0003-0006
- type: "observation"
- check_card: "CHK-0003-0004"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty, not truncated, no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0005
- type: "check-card"
- doubt: "Was DSC_0142.ARW (65536 bytes, outside target) moved?"
- decision: "how DSC_0142.ARW is reported"
- operation: "D6 file-agent, size 65536, depth 8"
- outcomes: "candidates: hash; empty: missing"
- cost: "size-filtered listing"
- budget_left: 297

## RECORD OBS-0003-0007
- type: "observation"
- check_card: "CHK-0003-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "2 entries: raw/DSC_0101.ARW, raw/DSC_0150.ARW; not truncated, no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0006
- type: "check-card"
- doubt: "Are CPY-0001-0013, -0014, -0015 still in aurora-2026-10-01?"
- decision: "sources for copy.docx, cover.tif, layout.indd"
- operation: "D5 file-agent, 3 paths"
- outcomes: "inside root: hash; else: aurora-2026-11-05"
- cost: "metadata"
- budget_left: 297

## RECORD OBS-0003-0008
- type: "observation"
- check_card: "CHK-0003-0006"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "present, readable, real path equal: copy.docx 968, cover.tif 9396, layout.indd 16384, mtime 1200 each"
- coverage: "3 of 3 paths"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0007
- type: "check-card"
- doubt: "Do they still hold VER-0001-0002, -0003, -0006?"
- decision: "whether they are the rebuild sources"
- operation: "D7 file-agent, 3 files"
- outcomes: "equal: source; differs: next location"
- cost: "digest of 26748 bytes"
- budget_left: 297

## RECORD OBS-0003-0009
- type: "observation"
- check_card: "CHK-0003-0007"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "copy.docx, cover.tif, layout.indd equal to VER-0001-0002, VER-0001-0003, VER-0001-0006"
- coverage: "3 of 3 hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0003-0008
- type: "check-card"
- doubt: "Does a 65536-byte candidate hold VER-0001-0010?"
- decision: "DSC_0142.ARW moved or missing"
- operation: "D7 file-agent, 2 files"
- outcomes: "equal: moved; own versions: missing"
- cost: "digest of 131072 bytes"
- budget_left: 294

## RECORD OBS-0003-0010
- type: "observation"
- check_card: "CHK-0003-0008"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "raw/DSC_0101.ARW equal VER-0001-0009, raw/DSC_0150.ARW equal VER-0001-0011; neither is VER-0001-0010"
- coverage: "2 of 2 hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0003-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "moved"
- located_at: "/data/studio/projects/aurora/brief-FINAL.pdf"
- statement: "brief.pdf absent at its path; VER-0001-0001 found at brief-FINAL.pdf"
- class: "observed"
- supports: ["OBS-0003-0003", "OBS-0003-0004"]
- contradicts: []
- depends_on: ["VER-0001-0001", "OBS-0003-0004"]
- status: "current"

## RECORD CLM-0003-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "missing"
- located_at: null
- statement: "absent; size search complete to depth 8, no candidate"
- class: "observed"
- supports: ["OBS-0003-0003", "OBS-0003-0005"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0003-0005"]
- status: "current"

## RECORD CLM-0003-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "altered"
- located_at: null
- statement: "same size and mtime, digest differs from VER-0001-0003"
- class: "observed"
- supports: ["OBS-0003-0004"]
- contradicts: []
- depends_on: ["VER-0001-0003", "OBS-0003-0004"]
- status: "current"

## RECORD CLM-0003-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "absent; size search complete to depth 8, no candidate"
- class: "observed"
- supports: ["OBS-0003-0003", "OBS-0003-0006"]
- contradicts: []
- depends_on: ["VER-0001-0006", "OBS-0003-0006"]
- status: "current"

## RECORD CLM-0003-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: null
- statement: "digest equal to VER-0001-0007"
- class: "observed"
- supports: ["OBS-0003-0004"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0003-0004"]
- status: "current"

## RECORD CLM-0003-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "missing"
- located_at: null
- statement: "absent; both size-matched candidates hold other versions"
- class: "observed"
- supports: ["OBS-0003-0003", "OBS-0003-0007", "OBS-0003-0010"]
- contradicts: []
- depends_on: ["VER-0001-0010", "OBS-0003-0010"]
- status: "current"

## RECORD CLM-0003-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009, AST-0001-0011"
- asset_state: "intact"
- located_at: null
- statement: "digests equal to their recorded versions"
- class: "observed"
- supports: ["OBS-0003-0010"]
- contradicts: []
- depends_on: ["VER-0001-0009", "VER-0001-0011", "OBS-0003-0010"]
- status: "current"

## RECORD CLM-0003-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004, AST-0001-0005, AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: null
- statement: "present with recorded size and mtime; not hashed"
- class: "observed"
- supports: ["OBS-0003-0003"]
- contradicts: []
- depends_on: ["OBS-0003-0003"]
- status: "current"

## RECORD CLM-0003-0009
- type: "claim"
- kind: "cause"
- subject: "CAS-0003"
- statement: "cause unknown: no source states one"
- class: "unknown"
- supports: []
- contradicts: []
- depends_on: []
- status: "current"

## RECORD CLM-0003-0010
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0001, CPY-0001-0002, CPY-0001-0003, CPY-0001-0006, CPY-0001-0010"
- statement: "these project copies no longer hold their version: 4 absent, cover.tif differs"
- class: "contradicted"
- supports: ["OBS-0003-0003", "OBS-0003-0004"]
- contradicts: ["CPY-0001-0001", "CPY-0001-0002", "CPY-0001-0003", "CPY-0001-0006", "CPY-0001-0010"]
- depends_on: ["OBS-0003-0003", "OBS-0003-0004"]
- status: "current"

## RECORD CLM-0003-0011
- type: "claim"
- kind: "contradiction"
- subject: "APR-0002-01"
- statement: "APR-0002-01 plan_sha256 differs from the digest of plan file CERBERO-B-0002-02.md now (OBS-0003-0002) and in IDX-0002-01; RCP-0002-01 is not used as recovery evidence"
- class: "contradicted"
- supports: ["OBS-0003-0002"]
- contradicts: ["APR-0002-01"]
- depends_on: ["APR-0002-01", "OBS-0003-0002"]
- status: "current"

## RECORD CPY-0003-0001
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/data/studio/projects/aurora/brief.pdf"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0003-0003"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0001"

## RECORD CPY-0003-0002
- type: "copy"
- version_id: "VER-0001-0002"
- real_path: "/data/studio/projects/aurora/copy.docx"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0003-0003"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0002"

## RECORD CPY-0003-0003
- type: "copy"
- version_id: "VER-0001-0003"
- real_path: "/data/studio/projects/aurora/cover.tif"
- location_id: "LOC-0001-0001"
- sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- observation: "OBS-0003-0004"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0003"

## RECORD CPY-0003-0004
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0003-0003"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD CPY-0003-0005
- type: "copy"
- version_id: "VER-0001-0010"
- real_path: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0003-0003"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0010"

## RECORD CPY-0003-0006
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/data/studio/projects/aurora/brief-FINAL.pdf"
- location_id: "LOC-0001-0001"
- sha256: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- observation: "OBS-0003-0004"
- access: "readable"
- status: "current"

## RECORD OPN-0003-0001
- type: "open-item"
- subject: "AST-0001-0010"
- reason: "outside the target: missing; no copy of VER-0001-0010 recorded in the named locations (CAS-0001), not re-searched now"
- needed_to_resolve: "a request that names this file"

## RECORD PLN-0003-01
- type: "plan"
- case_id: "CAS-0003"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/data/studio/recovered/cerbero-rebuild-CAS-0003"
- goal: "full rebuild of SET-0001-0002 (Delivery 2): all 5 members, intact ones included"
- preconditions: "user confirmed plan ID, saved digest and SET-0001-0002; plan file unchanged before the first change; NAS approvals answered by the user; per entry: source inside its root and re-hashed equal to expected_sha256 just before copying; destination absent, inside the rebuild folder"
- success_conditions: "per entry: destination at the planned real path, digest equal to expected_sha256 and to the source read before copying; documents read whole by document-agent where available; complete only when all 5 members are verified there"
- risks: "no atomic copy; sources may change; approvals may be declined; equal digests do not show absence of malware; no format check for .tif, .indd, .ai; rebuilt files are not a new backup copy"
- pending: []
- previous_receipt: null
- supersedes_plan: null
- target_kind: "full-rebuild"
- target_members: ["AST-0001-0001", "AST-0001-0002", "AST-0001-0003", "AST-0001-0006", "AST-0001-0007"]
- outside_target: ["AST-0001-0010"]

## RECORD ENT-0003-01-01
- type: "plan-entry"
- plan_id: "PLN-0003-01"
- asset_id: "AST-0001-0001"
- name: "brief.pdf"
- version_id: "VER-0001-0001"
- expected_sha256: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- size_bytes: 736
- source_path: "/data/studio/projects/aurora/brief-FINAL.pdf"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/brief.pdf"

## RECORD ENT-0003-01-02
- type: "plan-entry"
- plan_id: "PLN-0003-01"
- asset_id: "AST-0001-0002"
- name: "copy.docx"
- version_id: "VER-0001-0002"
- expected_sha256: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- size_bytes: 968
- source_path: "/data/studio/backups/aurora-2026-10-01/copy.docx"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/copy.docx"

## RECORD ENT-0003-01-03
- type: "plan-entry"
- plan_id: "PLN-0003-01"
- asset_id: "AST-0001-0003"
- name: "cover.tif"
- version_id: "VER-0001-0003"
- expected_sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- size_bytes: 9396
- source_path: "/data/studio/backups/aurora-2026-10-01/cover.tif"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/cover.tif"

## RECORD ENT-0003-01-04
- type: "plan-entry"
- plan_id: "PLN-0003-01"
- asset_id: "AST-0001-0006"
- name: "layout.indd"
- version_id: "VER-0001-0006"
- expected_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- size_bytes: 16384
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/layout.indd"

## RECORD ENT-0003-01-05
- type: "plan-entry"
- plan_id: "PLN-0003-01"
- asset_id: "AST-0001-0007"
- name: "logo.ai"
- version_id: "VER-0001-0007"
- expected_sha256: "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"
- size_bytes: 8192
- source_path: "/data/studio/projects/aurora/logo.ai"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/logo.ai"