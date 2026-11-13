# CERBERO BUNDLE B-0002-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-01"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0002
- type: "case"
- scope_id: "SCP-0001"
- request: "I lost files from project Aurora. Find what happened, recover the correct versions of Delivery 2 that are available, and tell me what you could not recover."
- status: "open"
- opened_in: "this session"

## RECORD STM-0002-0001
- type: "statement"
- text: "I lost files from project Aurora. Find what happened, recover the correct versions of Delivery 2 that are available, and tell me what you could not recover. Project folder: /volume1/studio/projects/aurora. Cerbero memory folder: /volume1/studio/cerbero-memory. Copy locations: /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora. Create the recovery folder under /volume1/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD OBS-0002-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D1"
- state: "completed"
- result: "current user folder real path /volume1/studio"
- coverage: "1 of 1"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "exists, readable, real path equal to the given path: /volume1/studio/projects/aurora, /volume1/studio/cerbero-memory, /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05, /volume1/studio/usb-archive/aurora, /volume1/studio/recovered. /volume1/studio: exists false, reason not found"
- coverage: "7 of 7 folders"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "2 files: /volume1/studio/cerbero-memory/CERBERO-B-0001-01.md 20963 bytes mtime 3001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md 383 bytes mtime 3002"
- coverage: "truncated false, 2 entries, limit 200"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D4"
- state: "completed"
- result: "read CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md; no file reported missing, unreadable or partial; B-0001-01 parsed as cerbero-memory-2 with 79 records and no dangling reference"
- coverage: "2 of 2 files"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0005
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 0589d203a592b05653d6b2c36b37879bd62506966497a4ecc54c887061744c0d 20963 bytes, matches index IDX-0001-01-0001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md sha256 d48d2e2b404273c949663bc149a568d1f42a680b6c73f73cf1576fa37bfbf41b 383 bytes"
- coverage: "2 of 2 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0001
- type: "check-card"
- doubt: "Are the 11 recorded assets of SCP-0001 present at their recorded paths with recorded size and mtime?"
- decision: "which assets need a digest and which need a search"
- operation: "D5 file-agent"
- outcomes: "same size and time: digest for critical assets, intact-metadata for ordinary; different: digest; missing: exact-size search in scope"
- cost: "metadata of 11 paths, read-only"
- budget_left: 298

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "not_found: /volume1/studio/projects/aurora/brief.pdf, /volume1/studio/projects/aurora/copy.docx, /volume1/studio/projects/aurora/layout.indd, /volume1/studio/projects/aurora/raw/DSC_0142.ARW. Present, readable, real path equal, size and mtime equal to the asset record: cover.tif 32768/1103, logo.ai 8192/900, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, palette.ase 512/900, raw/DSC_0101.ARW 65536/800, raw/DSC_0150.ARW 65536/802"
- coverage: "11 of 11 recorded asset paths"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Are cover.tif and logo.ai at their recorded paths still VER-0001-0003 and VER-0001-0007?"
- decision: "whether these Delivery 2 members need recovery"
- operation: "D7 file-agent"
- outcomes: "digest equal: intact; digest differs: altered"
- cost: "2 digests, 40960 bytes, read-only"
- budget_left: 298

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/projects/aurora/cover.tif sha256 93bffe5d03dc8c751aec64a596713512cdb2369b4227d2bc4412a45c01867275 32768 bytes, matches expected false; /volume1/studio/projects/aurora/logo.ai sha256 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 bytes, matches expected true"
- coverage: "2 of 2 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Is brief.pdf (4096 bytes) present elsewhere inside the project?"
- decision: "moved inside scope or absent"
- operation: "D6 file-agent, size exactly 4096, depth 8"
- outcomes: "unrecorded candidate of that size: hash it; complete empty result: not in scope"
- cost: "1 listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "2 files: /volume1/studio/projects/aurora/brief-FINAL.pdf 4096 bytes mtime 1100; /volume1/studio/projects/aurora/exports/previews/cover-preview.jpg 4096 bytes mtime 1104"
- coverage: "complete to depth 8: 2 entries under limit 200, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Is copy.docx (6144 bytes) present elsewhere inside the project?"
- decision: "moved inside scope or absent"
- operation: "D6 file-agent, size exactly 6144, depth 8"
- outcomes: "candidate: hash it; complete empty result: not in scope"
- cost: "1 listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty: no regular file of 6144 bytes under /volume1/studio/projects/aurora"
- coverage: "complete to depth 8: 0 entries, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Is layout.indd (16384 bytes) present elsewhere inside the project?"
- decision: "moved inside scope or absent"
- operation: "D6 file-agent, size exactly 16384, depth 8"
- outcomes: "candidate: hash it; complete empty result: not in scope"
- cost: "1 listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0010
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty: no regular file of 16384 bytes under /volume1/studio/projects/aurora"
- coverage: "complete to depth 8: 0 entries, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0006
- type: "check-card"
- doubt: "Is raw/DSC_0142.ARW (65536 bytes) present elsewhere inside the project?"
- decision: "moved inside scope or absent"
- operation: "D6 file-agent, size exactly 65536, depth 8"
- outcomes: "candidate: hash it; complete empty result: not in scope"
- cost: "1 listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0011
- type: "observation"
- check_card: "CHK-0002-0006"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "2 files: /volume1/studio/projects/aurora/raw/DSC_0101.ARW 65536 bytes mtime 800; /volume1/studio/projects/aurora/raw/DSC_0150.ARW 65536 bytes mtime 802"
- coverage: "complete to depth 8: 2 entries under limit 200, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0007
- type: "check-card"
- doubt: "Does any size-matched candidate in the project hold VER-0001-0001 (brief.pdf) or VER-0001-0010 (DSC_0142.ARW)?"
- decision: "brief.pdf and DSC_0142.ARW: moved inside scope or absent"
- operation: "D7 file-agent on brief-FINAL.pdf, raw/DSC_0101.ARW, raw/DSC_0150.ARW"
- outcomes: "brief-FINAL.pdf equal to VER-0001-0001: brief.pdf moved; a raw file equal to VER-0001-0010: DSC_0142 content present at another path; otherwise absent in scope"
- cost: "3 digests, 135168 bytes, read-only"
- budget_left: 296

## RECORD OBS-0002-0012
- type: "observation"
- check_card: "CHK-0002-0007"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/projects/aurora/brief-FINAL.pdf sha256 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 bytes, matches VER-0001-0001 true; /volume1/studio/projects/aurora/raw/DSC_0101.ARW sha256 2cca9c67186306e2378e0aae5ef4c7b8306eee635c7343e3fd8a500679cb5442 65536 bytes, matches VER-0001-0009 true; /volume1/studio/projects/aurora/raw/DSC_0150.ARW sha256 88e99368f265eba2034cc29141ca1f3e738cf2c93abfd29e4404dc6ec07a6004 65536 bytes, matches VER-0001-0011 true"
- coverage: "3 of 3 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0008
- type: "check-card"
- doubt: "Do the recorded copies CPY-0001-0015, CPY-0001-0013 and CPY-0001-0014 still exist inside /volume1/studio/backups/aurora-2026-10-01?"
- decision: "sources for layout.indd, copy.docx and cover.tif of Delivery 2"
- operation: "D5 file-agent"
- outcomes: "present with real path inside the root and version size: hash; missing or outside: try the next location"
- cost: "metadata of 3 paths, read-only"
- budget_left: 293

## RECORD OBS-0002-0013
- type: "observation"
- check_card: "CHK-0002-0008"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "present, readable, real path equal: /volume1/studio/backups/aurora-2026-10-01/copy.docx 6144 bytes mtime 1200; /volume1/studio/backups/aurora-2026-10-01/cover.tif 32768 bytes mtime 1200; /volume1/studio/backups/aurora-2026-10-01/layout.indd 16384 bytes mtime 1200"
- coverage: "3 of 3 paths"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0009
- type: "check-card"
- doubt: "Are those three backup files still VER-0001-0002, VER-0001-0003 and VER-0001-0006?"
- decision: "whether they can serve as recovery sources"
- operation: "D7 file-agent with expected digests"
- outcomes: "equal: eligible source verified now; differs: contradiction, try 2026-11-05 or the USB archive"
- cost: "3 digests, 55296 bytes, read-only"
- budget_left: 293

## RECORD OBS-0002-0014
- type: "observation"
- check_card: "CHK-0002-0009"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/volume1/studio/backups/aurora-2026-10-01/copy.docx sha256 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 bytes, matches true; /volume1/studio/backups/aurora-2026-10-01/cover.tif sha256 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 bytes, matches true; /volume1/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b 16384 bytes, matches true"
- coverage: "3 of 3 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0010
- type: "check-card"
- doubt: "Is there any 65536-byte file, a possible copy of VER-0001-0010 (DSC_0142.ARW), in the three named copy locations?"
- decision: "whether DSC_0142.ARW can be recovered"
- operation: "D6 file-agent, size exactly 65536, depth 8, in each copy location"
- outcomes: "candidates: hash them; complete empty results: no copy in the named locations"
- cost: "3 listings, read-only"
- budget_left: 290

## RECORD OBS-0002-0015
- type: "observation"
- check_card: "CHK-0002-0010"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty: no regular file of 65536 bytes under /volume1/studio/backups/aurora-2026-10-01"
- coverage: "complete to depth 8: 0 entries, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0016
- type: "observation"
- check_card: "CHK-0002-0010"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty: no regular file of 65536 bytes under /volume1/studio/backups/aurora-2026-11-05"
- coverage: "complete to depth 8: 0 entries, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0017
- type: "observation"
- check_card: "CHK-0002-0010"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty: no regular file of 65536 bytes under /volume1/studio/usb-archive/aurora"
- coverage: "complete to depth 8: 0 entries, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0002-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "moved"
- located_at: "/volume1/studio/projects/aurora/brief-FINAL.pdf"
- statement: "brief.pdf is absent at its recorded path; /volume1/studio/projects/aurora/brief-FINAL.pdf has the digest of approved version VER-0001-0001; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0012"]
- contradicts: []
- depends_on: ["VER-0001-0001", "OBS-0002-0012"]
- status: "current"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "missing"
- located_at: null
- statement: "copy.docx is absent at its recorded path and no 6144-byte file exists in the project to depth 8; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0002-0009"]
- status: "current"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "altered"
- located_at: "/volume1/studio/projects/aurora/cover.tif"
- statement: "cover.tif at its recorded path keeps the recorded size and mtime but its digest differs from approved version VER-0001-0003 and from VER-0001-0015; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: ["CPY-0001-0003"]
- depends_on: ["VER-0001-0003", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "layout.indd is absent at its recorded path and no 16384-byte file exists in the project to depth 8; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0010"]
- contradicts: []
- depends_on: ["VER-0001-0006", "OBS-0002-0010"]
- status: "current"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/logo.ai"
- statement: "logo.ai at its recorded path has the digest of approved version VER-0001-0007"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/exports/previews/cover-preview.jpg"
- statement: "cover-preview.jpg has the recorded size and mtime; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/fonts-license.pdf"
- statement: "fonts-license.pdf has the recorded size and mtime; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/palette.ase"
- statement: "palette.ase has the recorded size and mtime; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/raw/DSC_0101.ARW"
- statement: "raw/DSC_0101.ARW has the digest of VER-0001-0009"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0012"]
- contradicts: []
- depends_on: ["VER-0001-0009", "OBS-0002-0012"]
- status: "current"

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "missing"
- located_at: null
- statement: "raw/DSC_0142.ARW is absent at its recorded path; the only 65536-byte files in the project are DSC_0101.ARW and DSC_0150.ARW with their own versions; no 65536-byte file exists in the three named copy locations to depth 8; not recoverable with the sources available; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0011", "OBS-0002-0012", "OBS-0002-0015", "OBS-0002-0016", "OBS-0002-0017"]
- contradicts: []
- depends_on: ["VER-0001-0010", "OBS-0002-0011", "OBS-0002-0015", "OBS-0002-0016", "OBS-0002-0017"]
- status: "current"

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/raw/DSC_0150.ARW"
- statement: "raw/DSC_0150.ARW has the digest of VER-0001-0011"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0012"]
- contradicts: []
- depends_on: ["VER-0001-0011", "OBS-0002-0012"]
- status: "current"

## RECORD CLM-0002-0012
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0003"
- statement: "CPY-0001-0003 records /volume1/studio/projects/aurora/cover.tif as VER-0001-0003 with sha256 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef (OBS-0001-0006); D7 now returns 93bffe5d03dc8c751aec64a596713512cdb2369b4227d2bc4412a45c01867275 (OBS-0002-0007)"
- class: "contradicted"
- supports: ["OBS-0002-0007"]
- contradicts: ["OBS-0001-0006", "CPY-0001-0003"]
- depends_on: ["CPY-0001-0003", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0013
- type: "claim"
- kind: "copy-state"
- subject: "CPY-0001-0013, CPY-0001-0014, CPY-0001-0015"
- statement: "the copies of VER-0001-0002, VER-0001-0003 and VER-0001-0006 in /volume1/studio/backups/aurora-2026-10-01 were re-observed in this session with matching digests (verified-now)"
- class: "observed"
- supports: ["OBS-0002-0013", "OBS-0002-0014"]
- contradicts: []
- depends_on: ["CPY-0001-0013", "CPY-0001-0014", "CPY-0001-0015", "OBS-0002-0014"]
- status: "current"

## RECORD CLM-0002-0014
- type: "claim"
- kind: "path-state"
- subject: "/volume1/studio"
- statement: "D1 returned /volume1/studio as the real path of the current user folder, while D2 reported /volume1/studio as not found; not used by any step of this case"
- class: "contradicted"
- supports: ["OBS-0002-0001"]
- contradicts: ["OBS-0002-0002"]
- depends_on: ["OBS-0002-0001", "OBS-0002-0002"]
- status: "current"

## RECORD CPY-0002-0001
- type: "copy"
- version_id: "VER-0001-0003"
- real_path: "/volume1/studio/projects/aurora/cover.tif"
- location_id: "LOC-0001-0001"
- sha256: "93bffe5d03dc8c751aec64a596713512cdb2369b4227d2bc4412a45c01867275"
- observation: "OBS-0002-0007"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0003"

## RECORD CPY-0002-0002
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/volume1/studio/projects/aurora/brief.pdf"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0001"

## RECORD CPY-0002-0003
- type: "copy"
- version_id: "VER-0001-0002"
- real_path: "/volume1/studio/projects/aurora/copy.docx"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0002"

## RECORD CPY-0002-0004
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/volume1/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD CPY-0002-0005
- type: "copy"
- version_id: "VER-0001-0010"
- real_path: "/volume1/studio/projects/aurora/raw/DSC_0142.ARW"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0010"

## RECORD CPY-0002-0006
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/volume1/studio/projects/aurora/brief-FINAL.pdf"
- location_id: "LOC-0001-0001"
- sha256: "9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"
- observation: "OBS-0002-0012"
- access: "readable"
- status: "current"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0001"
- text: "brief.pdf was renamed or moved to brief-FINAL.pdf inside the project"
- status: "supported"
- for: ["OBS-0002-0006", "OBS-0002-0012"]
- against: []
- next_check: "who renamed it and why is unknown; only a user statement or a cited project note could say whether the rename was intended"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0002, AST-0001-0006"
- text: "copy.docx and layout.indd are absent from the project with copies elsewhere"
- status: "supported"
- for: ["OBS-0002-0006", "OBS-0002-0009", "OBS-0002-0010", "OBS-0002-0014"]
- against: []
- next_check: "presence deeper than depth 8 or outside the named folders was not reviewed"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0010"
- text: "raw/DSC_0142.ARW is absent without a copy in the named locations"
- status: "supported"
- for: ["OBS-0002-0006", "OBS-0002-0011", "OBS-0002-0012", "OBS-0002-0015", "OBS-0002-0016", "OBS-0002-0017"]
- against: []
- next_check: "another location the NAS can read, named by the user"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "CAS-0002"
- text: "cause of the rename, the removals and the change of cover.tif content"
- status: "undetermined"
- for: []
- against: []
- next_check: "no source states a cause; a user statement or a cited document would be needed"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "AST-0001-0010"
- reason: "raw/DSC_0142.ARW is missing and no copy was found in the four named locations; it is not in any approved set"
- needed_to_resolve: "a further location the NAS can read that holds a copy, named by the user"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "CAS-0002"
- reason: "cause of the changes unknown"
- needed_to_resolve: "a user statement or a cited source"

## RECORD OPN-0002-0003
- type: "open-item"
- subject: "LOC-0001-0002, LOC-0001-0003"
- reason: "STM-0001-0003 places both backup folders on Volume 2, while the NAS real paths of these folders begin with /volume1; a path namespace is not proof of a disk layout, but the declaration should be checked"
- needed_to_resolve: "the user confirms or corrects the volume of each location before a What-if evaluation relies on it"

## RECORD OPN-0002-0004
- type: "open-item"
- subject: "SCP-0001"
- reason: "files added to the project since the baseline were not inventoried; nothing deeper than depth 8 was reviewed; the asset record of brief.pdf still names its old path"
- needed_to_resolve: "a new Baseline after recovery, if the user wants it"

## RECORD OPN-0002-0005
- type: "open-item"
- subject: "/volume1/studio"
- reason: "D1 and D2 disagree on whether /volume1/studio exists (CLM-0002-0014)"
- needed_to_resolve: "not needed for this case"

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/volume1/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "Recover the members of approved set SET-0001-0002 (Delivery 2) that are missing or altered: layout.indd VER-0001-0006, copy.docx VER-0001-0002 and cover.tif VER-0001-0003, copied from /volume1/studio/backups/aurora-2026-10-01 into the new folder /volume1/studio/recovered/cerbero-recovery-CAS-0002. brief.pdf VER-0001-0001 is moved inside the project to /volume1/studio/projects/aurora/brief-FINAL.pdf and logo.ai VER-0001-0007 is intact; neither is copied. Operations: create the recovery folder (no subfolders); copy each source to its destination, never move, never overwrite."
- preconditions: "Per entry: the user confirmed plan PLN-0002-01 with its saved digest and reconfirmed SET-0001-0002; the operation (mkdir, cpmv in copy mode without overwrite) is in the capability evidence and the expert reports it allowed; the source real path lies inside /volume1/studio/backups/aurora-2026-10-01 and its digest, observed again immediately before copying, equals expected_sha256; the destination does not exist and lies inside /volume1/studio/recovered/cerbero-recovery-CAS-0002; immediately before the first change the saved plan file digest equals the confirmed digest."
- success_conditions: "Per entry: the destination exists at the planned real path returned by the NAS and its digest equals expected_sha256."
- risks: "Sources may change between the check and the copy; no atomic copy and no rollback of the set; the project, the copies and this memory are on the same NAS and are not an independent root of trust; the cause of the changes is unknown; altered cover.tif stays at its original path for comparison."
- pending: ["raw/DSC_0142.ARW (AST-0001-0010, VER-0001-0010): no-source; missing, no copy in the four named locations; not in any approved set; not recoverable with the sources available", "brief.pdf (AST-0001-0001): moved to /volume1/studio/projects/aurora/brief-FINAL.pdf with the VER-0001-0001 digest; not copied", "logo.ai (AST-0001-0007): intact; not copied", "cause of the changes: unknown"]
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

## RECORD ENT-0002-01-02
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0002"
- name: "copy.docx"
- version_id: "VER-0001-0002"
- expected_sha256: "0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"
- size_bytes: 6144
- source_path: "/volume1/studio/backups/aurora-2026-10-01/copy.docx"
- destination_path: "/volume1/studio/recovered/cerbero-recovery-CAS-0002/copy.docx"

## RECORD ENT-0002-01-03
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0003"
- name: "cover.tif"
- version_id: "VER-0001-0003"
- expected_sha256: "2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"
- size_bytes: 32768
- source_path: "/volume1/studio/backups/aurora-2026-10-01/cover.tif"
- destination_path: "/volume1/studio/recovered/cerbero-recovery-CAS-0002/cover.tif"
