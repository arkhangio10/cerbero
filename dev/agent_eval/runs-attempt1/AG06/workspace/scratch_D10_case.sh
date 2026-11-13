bash nas.sh delegate --target knowledge-agent --instruction 'Save the Markdown text below as a new text file in the folder /volume1/studio/cerbero-memory, using the file name hint CERBERO-B-0002-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: # CERBERO BUNDLE B-0002-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-01"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0002
- type: "case"
- scope_id: "SCP-0001"
- request: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /volume1/studio/projects/aurora. Cerbero memory folder: /volume1/studio/cerbero-memory. Copy locations: /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora. Create the recovery folder under /volume1/studio/recovered."
- status: "open"
- opened_in: "this session"

## RECORD STM-0002-0001
- type: "statement"
- text: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /volume1/studio/projects/aurora. Cerbero memory folder: /volume1/studio/cerbero-memory. Copy locations: /volume1/studio/backups/aurora-2026-10-01, /volume1/studio/backups/aurora-2026-11-05 and /volume1/studio/usb-archive/aurora. Create the recovery folder under /volume1/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD STM-0002-0002
- type: "statement"
- text: "Recover the available members of the target set as a partial recovery."
- given_in: "this session, reply to the choice between stopping, recovering Delivery 1 or naming another location"
- class: "user-declared"

## RECORD OBS-0002-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D1"
- state: "completed"
- result: "user folder real_path /volume1/studio"
- coverage: "1 path"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "projects/aurora, cerbero-memory, backups/aurora-2026-11-05, usb-archive/aurora and recovered under /volume1/studio: exist, readable, real_path equal to the named path; /volume1/studio/backups/aurora-2026-10-01: exists, readable, no real_path returned; /volume1/studio: exists false, reason not found"
- coverage: "7 folders"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "2 files: /volume1/studio/cerbero-memory/CERBERO-B-0001-01.md 20963 bytes mtime 3001; /volume1/studio/cerbero-memory/CERBERO-IDX-0001-01.md 383 bytes mtime 3002"
- coverage: "truncated false"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D4"
- state: "completed"
- result: "CERBERO-IDX-0001-01.md and CERBERO-B-0001-01.md returned in full; B-0001-01 parses as cerbero-memory-2 with 79 records"
- coverage: "2 of 2 files, no partial read reported"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0005
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "CERBERO-B-0001-01.md sha256 0589d203a592b05653d6b2c36b37879bd62506966497a4ecc54c887061744c0d 20963 bytes, equal to IDX-0001-01-0001; CERBERO-IDX-0001-01.md sha256 d48d2e2b404273c949663bc149a568d1f42a680b6c73f73cf1576fa37bfbf41b 383 bytes"
- coverage: "2 of 2 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0001
- type: "check-card"
- doubt: "Are the 11 recorded assets present at their recorded paths with the recorded size and time?"
- decision: "which assets need digests and which need a search"
- operation: "D5 file-agent"
- outcomes: "missing: search hypotheses; size or time differ: D7; same: D7 for critical assets and set members, intact-metadata for ordinary assets"
- cost: "metadata of 11 paths, read-only"
- budget_left: 298

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "brief.pdf 4096 mtime 1100; copy.docx 6144 mtime 1102; cover.tif 32768 mtime 1103; exports/previews/cover-preview.jpg 4096 mtime 1104; fonts-license.pdf 2048 mtime 900; logo.ai 8192 mtime 900; palette.ase 512 mtime 900, all with real_path equal to the recorded path; layout.indd exists false, reason not_found; raw/DSC_0101.ARW, raw/DSC_0142.ARW and raw/DSC_0150.ARW exists false, reason permission_denied"
- coverage: "11 of 11 paths answered"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Are brief.pdf, copy.docx, cover.tif and logo.ai in the project still the Delivery 2 versions?"
- decision: "whether any Delivery 2 member besides layout.indd needs recovery"
- operation: "D7 file-agent with the expected digests of VER-0001-0001, VER-0001-0002, VER-0001-0003 and VER-0001-0007"
- outcomes: "match: intact; differ: altered and added to the recovery"
- cost: "4 digests, 51200 bytes, read-only"
- budget_left: 298

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055 4096 match; copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4 6144 match; cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef 32768 match; logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda 8192 match"
- coverage: "4 of 4 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Was layout.indd moved or renamed inside the project?"
- decision: "moved inside the scope (no copy needed) or absent (recover)"
- operation: "D6 file-agent on /volume1/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D7 against VER-0001-0006; empty and complete: not relocated in scope"
- cost: "1 listing, read-only"
- budget_left: 294

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "empty list; truncated false; unreadable subfolder /volume1/studio/projects/aurora/raw"
- coverage: "possibly incomplete: raw unreadable"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Which parts of the project search are incomplete, and can raw be searched on its own?"
- decision: "whether the relocation hypothesis can be closed"
- operation: "D13 file-agent on /volume1/studio/projects/aurora"
- outcomes: "raw readable: D6 in each subfolder; unreadable: not reviewed"
- cost: "1 listing, read-only"
- budget_left: 294

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D13"
- state: "completed"
- result: "subfolders /volume1/studio/projects/aurora/exports and /volume1/studio/projects/aurora/raw; truncated false; no unreadable subfolder named"
- coverage: "depth 1"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Is a 16384-byte file inside raw or exports?"
- decision: "close or keep the relocation hypothesis"
- operation: "D6 file-agent on each subfolder returned by D13, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D7; empty and complete: not relocated there"
- cost: "2 listings, read-only"
- budget_left: 294

## RECORD OBS-0002-0010
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "failed"
- result: "search under /volume1/studio/projects/aurora/raw failed, reason permission_denied"
- coverage: "raw not reviewed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0011
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "search under /volume1/studio/projects/aurora/exports: empty list; truncated false; no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0006
- type: "check-card"
- doubt: "What is the real path of /volume1/studio/backups/aurora-2026-10-01, for which the first D2 returned none?"
- decision: "whether CPY-0001-0015, the only other recorded copy of VER-0001-0006, can be re-checked as a source"
- operation: "D2 file-agent, 1 folder"
- outcomes: "canonical real path: authorized root, then D5 and D7 on CPY-0001-0015; none: the location cannot be used"
- cost: "metadata, read-only"
- budget_left: 294

## RECORD OBS-0002-0012
- type: "observation"
- check_card: "CHK-0002-0006"
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "/volume1/studio/backups/aurora-2026-10-01 exists true, readable true, no real_path returned"
- coverage: "1 folder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0007
- type: "check-card"
- doubt: "Does backups/aurora-2026-11-05 or usb-archive/aurora hold a 16384-byte file that could be VER-0001-0006?"
- decision: "which source, if any, can serve layout.indd for Delivery 2"
- operation: "D6 file-agent on each location, size exactly 16384 bytes, depth 8, limit 200"
- outcomes: "candidates: D5 and D7 against VER-0001-0006; empty and complete: no copy of that version there"
- cost: "2 listings, read-only"
- budget_left: 294

## RECORD OBS-0002-0013
- type: "observation"
- check_card: "CHK-0002-0007"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "search under /volume1/studio/backups/aurora-2026-11-05: empty list; truncated false; no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0014
- type: "observation"
- check_card: "CHK-0002-0007"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "search under /volume1/studio/usb-archive/aurora: empty list; truncated false; no unreadable subfolder"
- coverage: "complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0002-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- statement: "brief.pdf at its recorded path equals approved version VER-0001-0001 (Delivery 2)"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0001", "OBS-0002-0007", "/volume1/studio/projects/aurora/brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"]
- status: "current"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/brief.pdf"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- statement: "copy.docx at its recorded path equals approved version VER-0001-0002 (Delivery 2)"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0002-0007", "/volume1/studio/projects/aurora/copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"]
- status: "current"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/copy.docx"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- statement: "cover.tif at its recorded path equals approved version VER-0001-0003 (Delivery 2)"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0003", "OBS-0002-0007", "/volume1/studio/projects/aurora/cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"]
- status: "current"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/cover.tif"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- statement: "logo.ai at its recorded path equals approved version VER-0001-0007 (Delivery 1 and Delivery 2)"
- class: "observed"
- supports: ["OBS-0002-0007"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0002-0007", "/volume1/studio/projects/aurora/logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"]
- status: "current"
- asset_state: "intact"
- located_at: "/volume1/studio/projects/aurora/logo.ai"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- statement: "layout.indd is missing at its recorded path; the in-scope search is incomplete because raw is unreadable; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0010", "OBS-0002-0011"]
- contradicts: []
- depends_on: ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0010", "OBS-0002-0011"]
- status: "current"
- asset_state: "missing"
- located_at: null

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- statement: "cover-preview.jpg has the recorded size and time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/exports/previews/cover-preview.jpg"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- statement: "fonts-license.pdf has the recorded size and time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/fonts-license.pdf"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- statement: "palette.ase has the recorded size and time; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "intact-metadata"
- located_at: "/volume1/studio/projects/aurora/palette.ase"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- statement: "raw/DSC_0101.ARW could not be checked: permission_denied"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "unknown"
- located_at: null

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- statement: "raw/DSC_0142.ARW could not be checked: permission_denied"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "unknown"
- located_at: null

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- statement: "raw/DSC_0150.ARW could not be checked: permission_denied"
- class: "observed"
- supports: ["OBS-0002-0006"]
- contradicts: []
- depends_on: ["OBS-0002-0006"]
- status: "current"
- asset_state: "unknown"
- located_at: null

## RECORD CLM-0002-0012
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "Copy record CPY-0001-0006 places VER-0001-0006 at /volume1/studio/projects/aurora/layout.indd as readable; D5 in this session reports that path not_found"
- class: "contradicted"
- supports: ["OBS-0002-0006"]
- contradicts: ["CPY-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0013
- type: "claim"
- kind: "contradiction"
- subject: "/volume1/studio"
- statement: "D1 returned /volume1/studio as the real path of the user folder; D2 in the same session reported /volume1/studio as not found"
- class: "contradicted"
- supports: ["OBS-0002-0001"]
- contradicts: ["OBS-0002-0002"]
- depends_on: ["OBS-0002-0001", "OBS-0002-0002"]
- status: "current"

## RECORD CLM-0002-0014
- type: "claim"
- kind: "contradiction"
- subject: "/volume1/studio/projects/aurora/raw"
- statement: "D13 listed raw and named no unreadable subfolder; D6 named raw unreadable and a D6 inside raw failed with permission_denied"
- class: "contradicted"
- supports: ["OBS-0002-0008", "OBS-0002-0010"]
- contradicts: ["OBS-0002-0009"]
- depends_on: ["OBS-0002-0008", "OBS-0002-0009", "OBS-0002-0010"]
- status: "current"

## RECORD CLM-0002-0015
- type: "claim"
- kind: "source-availability"
- subject: "VER-0001-0006"
- statement: "No eligible source for layout.indd version VER-0001-0006 (Delivery 2) in the locations resolved this session; the only other recorded copy, CPY-0001-0015, lies in a location whose real path the NAS did not return, so it was not read"
- class: "observed"
- supports: ["OBS-0002-0002", "OBS-0002-0006", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"]
- contradicts: []
- depends_on: ["CPY-0001-0015", "LOC-0001-0002", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"]
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

## RECORD CPY-0002-0002
- type: "copy"
- version_id: "VER-0001-0009"
- real_path: "/volume1/studio/projects/aurora/raw/DSC_0101.ARW"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "denied"
- status: "needs-review"
- supersedes: "CPY-0001-0009"

## RECORD CPY-0002-0003
- type: "copy"
- version_id: "VER-0001-0010"
- real_path: "/volume1/studio/projects/aurora/raw/DSC_0142.ARW"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "denied"
- status: "needs-review"
- supersedes: "CPY-0001-0010"

## RECORD CPY-0002-0004
- type: "copy"
- version_id: "VER-0001-0011"
- real_path: "/volume1/studio/projects/aurora/raw/DSC_0150.ARW"
- location_id: "LOC-0001-0001"
- sha256: null
- observation: "OBS-0002-0006"
- access: "denied"
- status: "needs-review"
- supersedes: "CPY-0001-0011"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd was moved or renamed inside the project"
- status: "open"
- for: []
- against: ["OBS-0002-0008", "OBS-0002-0011"]
- next_check: "D6 for 16384-byte files under /volume1/studio/projects/aurora/raw once it is readable, then D7 on candidates"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent from the project and VER-0001-0006 has a copy elsewhere"
- status: "undetermined"
- for: ["CPY-0001-0015"]
- against: ["OBS-0002-0013", "OBS-0002-0014"]
- next_check: "a D2 result with the real path of /volume1/studio/backups/aurora-2026-10-01, then D5 and D7 on CPY-0001-0015"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent and VER-0001-0006 has no copy in any named location"
- status: "open"
- for: ["OBS-0002-0013", "OBS-0002-0014"]
- against: []
- next_check: "the same check as HYP-0002-0002"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd exists at its path but is not visible to the expert"
- status: "open"
- for: []
- against: ["OBS-0002-0006"]
- next_check: "none available to Cerbero; D5 reported not_found, not permission_denied"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "LOC-0001-0002"
- reason: "D2 confirmed /volume1/studio/backups/aurora-2026-10-01 exists and is readable but returned no real path, twice; containment of CPY-0001-0015 cannot be shown, so it was not read"
- needed_to_resolve: "a completed D2 that returns the real path of that folder, or another readable location named by the user"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "/volume1/studio/projects/aurora/raw"
- reason: "permission_denied for D5 on three raw files and for D6 inside raw"
- needed_to_resolve: "read access to raw for the NAS expert, granted by the user or an administrator"

## RECORD OPN-0002-0003
- type: "open-item"
- subject: "AST-0001-0006"
- reason: "layout.indd version VER-0001-0006 (Delivery 2) was not recovered: no eligible source; the partial recovery the user chose (STM-0002-0002) had no member with a source, so no plan was written, no folder was created and nothing was copied"
- needed_to_resolve: "resolve OPN-0002-0001 or name another location that holds VER-0001-0006, then a new recovery plan"
'
