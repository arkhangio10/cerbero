# CERBERO BUNDLE B-0001-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0001-01"
- case_id: "CAS-0001"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0001
- type: "case"
- scope_id: "SCP-0001"
- request: "baseline"
- status: "open"
- opened_in: "this session"

## RECORD STM-0001-0001
- type: "statement"
- text: "Cerbero may read projects/aurora and the copy folders backups/aurora-2026-10-01, backups/aurora-2026-11-05, usb-archive/aurora, and save notes in cerbero-memory."
- given_in: "this session"
- class: "user-declared"

## RECORD STM-0001-0002
- type: "statement"
- text: "These files are critical: brief.pdf, copy.docx, cover.tif, layout.indd, logo.ai."
- given_in: "this session"
- class: "user-declared"

## RECORD STM-0001-0003
- type: "statement"
- text: "Delivery 2 (3 November) is the approved client delivery. The project folder is on Volume 1; both backup folders are on Volume 2 of this NAS. The USB archive is an external drive; I do not know its volume layout."
- given_in: "this session"
- class: "user-declared"

## RECORD DOM-0001-0001
- type: "domain"
- kind: "volume"
- label: "Volume 1"
- parent: "DOM-0001-0003"
- provenance: "STM-0001-0003"

## RECORD DOM-0001-0002
- type: "domain"
- kind: "volume"
- label: "Volume 2"
- parent: "DOM-0001-0003"
- provenance: "STM-0001-0003"

## RECORD DOM-0001-0003
- type: "domain"
- kind: "device"
- label: "this NAS"
- parent: null
- provenance: "STM-0001-0003"

## RECORD DOM-0001-0004
- type: "domain"
- kind: "device"
- label: "external USB drive"
- parent: null
- provenance: "STM-0001-0003"

## RECORD CHK-0001-0001
- type: "check-card"
- doubt: "Which files are in projects/aurora?"
- decision: "what the baseline records"
- operation: "D6 file-agent"
- outcomes: "entries: assets or copy candidates"
- cost: "full listing"
- budget_left: 300

## RECORD OBS-0001-0001
- type: "observation"
- check_card: "CHK-0001-0001"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "11 files, complete=True"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD LOC-0001-0001
- type: "location"
- real_root: "/data/studio/projects/aurora"
- memberships: {"volume": "DOM-0001-0001"}
- unknown_kinds: ["storage-pool", "site"]
- provenance: "STM-0001-0003"
- inventory: "complete"

## RECORD CHK-0001-0002
- type: "check-card"
- doubt: "Which files are in backups/aurora-2026-10-01?"
- decision: "what the baseline records"
- operation: "D6 file-agent"
- outcomes: "entries: assets or copy candidates"
- cost: "full listing"
- budget_left: 300

## RECORD OBS-0001-0002
- type: "observation"
- check_card: "CHK-0001-0002"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "5 files, complete=True"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD LOC-0001-0002
- type: "location"
- real_root: "/data/studio/backups/aurora-2026-10-01"
- memberships: {"volume": "DOM-0001-0002"}
- unknown_kinds: ["storage-pool", "site"]
- provenance: "STM-0001-0003"
- inventory: "complete"

## RECORD CHK-0001-0003
- type: "check-card"
- doubt: "Which files are in backups/aurora-2026-11-05?"
- decision: "what the baseline records"
- operation: "D6 file-agent"
- outcomes: "entries: assets or copy candidates"
- cost: "full listing"
- budget_left: 300

## RECORD OBS-0001-0003
- type: "observation"
- check_card: "CHK-0001-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "3 files, complete=True"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD LOC-0001-0003
- type: "location"
- real_root: "/data/studio/backups/aurora-2026-11-05"
- memberships: {"volume": "DOM-0001-0002"}
- unknown_kinds: ["storage-pool", "site"]
- provenance: "STM-0001-0003"
- inventory: "complete"

## RECORD CHK-0001-0004
- type: "check-card"
- doubt: "Which files are in usb-archive/aurora?"
- decision: "what the baseline records"
- operation: "D6 file-agent"
- outcomes: "entries: assets or copy candidates"
- cost: "full listing"
- budget_left: 300

## RECORD OBS-0001-0004
- type: "observation"
- check_card: "CHK-0001-0004"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "5 files, complete=True"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD LOC-0001-0004
- type: "location"
- real_root: "/data/studio/usb-archive/aurora"
- memberships: {"device": "DOM-0001-0004"}
- unknown_kinds: ["volume", "storage-pool", "site"]
- provenance: "STM-0001-0003"
- inventory: "complete"

## RECORD SCP-0001
- type: "scope"
- real_root: "/data/studio/projects/aurora"
- name: "aurora"
- authorized_by: "STM-0001-0001"
- newest_mtime: 1104

## RECORD OBS-0001-0005
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "11 project files hashed"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD STM-0001-0004
- type: "statement"
- text: "Delivery 1 is an approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai."
- given_in: "this session"
- class: "user-declared"

## RECORD STM-0001-0005
- type: "statement"
- text: "Delivery 2 is an approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai."
- given_in: "this session"
- class: "user-declared"

## RECORD AST-0001-0001
- type: "asset"
- scope_id: "SCP-0001"
- name: "brief.pdf"
- recorded_path: "/data/studio/projects/aurora/brief.pdf"
- importance: "critical"
- declared_by: "STM-0001-0002"
- current_version: "VER-0001-0001"
- recorded_size: 736
- recorded_mtime: 1100
- observation: "OBS-0001-0001"

## RECORD AST-0001-0002
- type: "asset"
- scope_id: "SCP-0001"
- name: "copy.docx"
- recorded_path: "/data/studio/projects/aurora/copy.docx"
- importance: "critical"
- declared_by: "STM-0001-0002"
- current_version: "VER-0001-0002"
- recorded_size: 968
- recorded_mtime: 1102
- observation: "OBS-0001-0001"

## RECORD AST-0001-0003
- type: "asset"
- scope_id: "SCP-0001"
- name: "cover.tif"
- recorded_path: "/data/studio/projects/aurora/cover.tif"
- importance: "critical"
- declared_by: "STM-0001-0002"
- current_version: "VER-0001-0003"
- recorded_size: 9396
- recorded_mtime: 1103
- observation: "OBS-0001-0001"

## RECORD AST-0001-0004
- type: "asset"
- scope_id: "SCP-0001"
- name: "cover-preview.jpg"
- recorded_path: "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0004"
- recorded_size: 4096
- recorded_mtime: 1104
- observation: "OBS-0001-0001"

## RECORD AST-0001-0005
- type: "asset"
- scope_id: "SCP-0001"
- name: "fonts-license.pdf"
- recorded_path: "/data/studio/projects/aurora/fonts-license.pdf"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0005"
- recorded_size: 2048
- recorded_mtime: 900
- observation: "OBS-0001-0001"

## RECORD AST-0001-0006
- type: "asset"
- scope_id: "SCP-0001"
- name: "layout.indd"
- recorded_path: "/data/studio/projects/aurora/layout.indd"
- importance: "critical"
- declared_by: "STM-0001-0002"
- current_version: "VER-0001-0006"
- recorded_size: 16384
- recorded_mtime: 1101
- observation: "OBS-0001-0001"

## RECORD AST-0001-0007
- type: "asset"
- scope_id: "SCP-0001"
- name: "logo.ai"
- recorded_path: "/data/studio/projects/aurora/logo.ai"
- importance: "critical"
- declared_by: "STM-0001-0002"
- current_version: "VER-0001-0007"
- recorded_size: 8192
- recorded_mtime: 900
- observation: "OBS-0001-0001"

## RECORD AST-0001-0008
- type: "asset"
- scope_id: "SCP-0001"
- name: "palette.ase"
- recorded_path: "/data/studio/projects/aurora/palette.ase"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0008"
- recorded_size: 512
- recorded_mtime: 900
- observation: "OBS-0001-0001"

## RECORD AST-0001-0009
- type: "asset"
- scope_id: "SCP-0001"
- name: "DSC_0101.ARW"
- recorded_path: "/data/studio/projects/aurora/raw/DSC_0101.ARW"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0009"
- recorded_size: 65536
- recorded_mtime: 800
- observation: "OBS-0001-0001"

## RECORD AST-0001-0010
- type: "asset"
- scope_id: "SCP-0001"
- name: "DSC_0142.ARW"
- recorded_path: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0010"
- recorded_size: 65536
- recorded_mtime: 801
- observation: "OBS-0001-0001"

## RECORD AST-0001-0011
- type: "asset"
- scope_id: "SCP-0001"
- name: "DSC_0150.ARW"
- recorded_path: "/data/studio/projects/aurora/raw/DSC_0150.ARW"
- importance: "ordinary"
- declared_by: "STM-0001-0001"
- current_version: "VER-0001-0011"
- recorded_size: 65536
- recorded_mtime: 802
- observation: "OBS-0001-0001"

## RECORD VER-0001-0001
- type: "version"
- asset_id: "AST-0001-0001"
- sha256: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- size_bytes: 736
- approved_by: "STM-0001-0005"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0002
- type: "version"
- asset_id: "AST-0001-0002"
- sha256: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- size_bytes: 968
- approved_by: "STM-0001-0005"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0003
- type: "version"
- asset_id: "AST-0001-0003"
- sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- size_bytes: 9396
- approved_by: "STM-0001-0005"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0004
- type: "version"
- asset_id: "AST-0001-0004"
- sha256: "ecc1dd1de6c6742c8418d86efc4be710cce0be8c8bd9fdf6d0c6b893c7ff03f0"
- size_bytes: 4096
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0005
- type: "version"
- asset_id: "AST-0001-0005"
- sha256: "c0a5a062646ea3d209d2c6b729c971ebfc5055081b110a5006e3315709cb3be8"
- size_bytes: 2048
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0006
- type: "version"
- asset_id: "AST-0001-0006"
- sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- size_bytes: 16384
- approved_by: "STM-0001-0005"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0007
- type: "version"
- asset_id: "AST-0001-0007"
- sha256: "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"
- size_bytes: 8192
- approved_by: "STM-0001-0005"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0008
- type: "version"
- asset_id: "AST-0001-0008"
- sha256: "2036ace748ccacffae3ce03cd2a001aefe53752abdcc5c4cb56044a48d22e6f6"
- size_bytes: 512
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0009
- type: "version"
- asset_id: "AST-0001-0009"
- sha256: "2cca9c67186306e2378e0aae5ef4c7b8306eee635c7343e3fd8a500679cb5442"
- size_bytes: 65536
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0010
- type: "version"
- asset_id: "AST-0001-0010"
- sha256: "2653339b90e2c2b0bd1cb1abbf34d1bbabb08e3ece0c62710a8d4ea177f4fe1a"
- size_bytes: 65536
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0011
- type: "version"
- asset_id: "AST-0001-0011"
- sha256: "88e99368f265eba2034cc29141ca1f3e738cf2c93abfd29e4404dc6ec07a6004"
- size_bytes: 65536
- approved_by: null
- observation: "OBS-0001-0005"

## RECORD VER-0001-0012
- type: "version"
- asset_id: "AST-0001-0001"
- sha256: "5a5200f29134b389cbe1301f04fec10a5f8a6a492c567c0bdc68d2264c545f37"
- size_bytes: 4096
- approved_by: "STM-0001-0004"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0013
- type: "version"
- asset_id: "AST-0001-0006"
- sha256: "708fb83dd6aa51f06ca314e7b469bf430d854b7f89c388e5a86a631032a9e71d"
- size_bytes: 15000
- approved_by: "STM-0001-0004"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0014
- type: "version"
- asset_id: "AST-0001-0002"
- sha256: "83d7903d7a7f770f2bafae46a3442f65474213c836ad8a9e7f8aef7ae3974dfa"
- size_bytes: 6000
- approved_by: "STM-0001-0004"
- observation: "OBS-0001-0005"

## RECORD VER-0001-0015
- type: "version"
- asset_id: "AST-0001-0003"
- sha256: "2f548bd1da38308b7d5dc7e8a742534dd3c73b99b6981133d2fb046a91f7d8c6"
- size_bytes: 32768
- approved_by: "STM-0001-0004"
- observation: "OBS-0001-0005"

## RECORD SET-0001-0001
- type: "approved-set"
- name: "Delivery 1"
- members: {"AST-0001-0001": "VER-0001-0012", "AST-0001-0006": "VER-0001-0013", "AST-0001-0002": "VER-0001-0014", "AST-0001-0003": "VER-0001-0015", "AST-0001-0007": "VER-0001-0007"}
- approved_by: "STM-0001-0004"
- status: "current"

## RECORD SET-0001-0002
- type: "approved-set"
- name: "Delivery 2"
- members: {"AST-0001-0001": "VER-0001-0001", "AST-0001-0006": "VER-0001-0006", "AST-0001-0002": "VER-0001-0002", "AST-0001-0003": "VER-0001-0003", "AST-0001-0007": "VER-0001-0007"}
- approved_by: "STM-0001-0005"
- status: "current"

## RECORD OBS-0001-0006
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "size-matched files hashed in projects/aurora"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD CPY-0001-0001
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/data/studio/projects/aurora/brief.pdf"
- location_id: "LOC-0001-0001"
- sha256: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0002
- type: "copy"
- version_id: "VER-0001-0002"
- real_path: "/data/studio/projects/aurora/copy.docx"
- location_id: "LOC-0001-0001"
- sha256: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0003
- type: "copy"
- version_id: "VER-0001-0003"
- real_path: "/data/studio/projects/aurora/cover.tif"
- location_id: "LOC-0001-0001"
- sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0004
- type: "copy"
- version_id: "VER-0001-0004"
- real_path: "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"
- location_id: "LOC-0001-0001"
- sha256: "ecc1dd1de6c6742c8418d86efc4be710cce0be8c8bd9fdf6d0c6b893c7ff03f0"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0005
- type: "copy"
- version_id: "VER-0001-0005"
- real_path: "/data/studio/projects/aurora/fonts-license.pdf"
- location_id: "LOC-0001-0001"
- sha256: "c0a5a062646ea3d209d2c6b729c971ebfc5055081b110a5006e3315709cb3be8"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0006
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0007
- type: "copy"
- version_id: "VER-0001-0007"
- real_path: "/data/studio/projects/aurora/logo.ai"
- location_id: "LOC-0001-0001"
- sha256: "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0008
- type: "copy"
- version_id: "VER-0001-0008"
- real_path: "/data/studio/projects/aurora/palette.ase"
- location_id: "LOC-0001-0001"
- sha256: "2036ace748ccacffae3ce03cd2a001aefe53752abdcc5c4cb56044a48d22e6f6"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0009
- type: "copy"
- version_id: "VER-0001-0009"
- real_path: "/data/studio/projects/aurora/raw/DSC_0101.ARW"
- location_id: "LOC-0001-0001"
- sha256: "2cca9c67186306e2378e0aae5ef4c7b8306eee635c7343e3fd8a500679cb5442"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0010
- type: "copy"
- version_id: "VER-0001-0010"
- real_path: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- location_id: "LOC-0001-0001"
- sha256: "2653339b90e2c2b0bd1cb1abbf34d1bbabb08e3ece0c62710a8d4ea177f4fe1a"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD CPY-0001-0011
- type: "copy"
- version_id: "VER-0001-0011"
- real_path: "/data/studio/projects/aurora/raw/DSC_0150.ARW"
- location_id: "LOC-0001-0001"
- sha256: "88e99368f265eba2034cc29141ca1f3e738cf2c93abfd29e4404dc6ec07a6004"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "current"

## RECORD OBS-0001-0007
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "size-matched files hashed in backups/aurora-2026-10-01"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"
