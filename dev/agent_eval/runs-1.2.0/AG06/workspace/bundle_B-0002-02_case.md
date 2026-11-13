# CERBERO BUNDLE B-0002-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-02"
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
- text: "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."
- given_in: "this session"
- class: "user-declared"

## RECORD STM-0002-0002
- type: "statement"
- text: "Recover the available members of the target set as a partial recovery."
- given_in: "this session"
- class: "user-declared"

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
- result: "real paths returned for /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio; /data/studio/backups/aurora-2026-10-01 reported existing and readable with no real path"
- coverage: "7 folders, 6 with real path"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0003
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "3 files: CERBERO-B-0001-01.md, CERBERO-B-0001-02.md, CERBERO-IDX-0001-01.md, real paths inside /data/studio/cerbero-memory"
- coverage: "not truncated, 3 of limit 200, complete"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0004
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "CERBERO-B-0001-01.md 8056343e9b83127a3cfa50579196f5d4787f2ac405c42be8b2a44bb186af1931 16684 bytes and CERBERO-B-0001-02.md bd00bb36e319d96ffd5a0b49353544a3d74c09d8d7f9fe7706b8c0e14d99d758 4403 bytes, both equal to index IDX-0001-01"
- coverage: "2 of 2 memory files hashed, counted apart from the session budget"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0001
- type: "check-card"
- doubt: "Are the recorded assets of the project still present with their recorded size and time?"
- decision: "which assets need a digest and which members of Delivery 2 need recovery"
- operation: "D5 file-agent on the 11 recorded asset paths"
- outcomes: "missing: test relocation and copies; changed metadata: digest; same metadata: digest for critical and set members, intact-metadata for ordinary"
- cost: "metadata of 11 paths, read-only"
- budget_left: 300

## RECORD OBS-0002-0005
- type: "observation"
- check_card: "CHK-0002-0001"
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "brief.pdf 4096/1100, copy.docx 6144/1102, cover.tif 32768/1103, logo.ai 8192/900, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, palette.ase 512/900: present with recorded size and time; layout.indd not_found; raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW permission_denied"
- coverage: "11 of 11 recorded asset paths checked"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0002
- type: "check-card"
- doubt: "Do the present Delivery 2 members still hold their approved versions?"
- decision: "whether brief.pdf, copy.docx, cover.tif and logo.ai need recovery"
- operation: "D7 file-agent with the Delivery 2 digests as expected"
- outcomes: "equal: intact; different: altered and recover"
- cost: "digest of 4 files, 51200 bytes, read-only"
- budget_left: 300

## RECORD OBS-0002-0006
- type: "observation"
- check_card: "CHK-0002-0002"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055, copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4, cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef, logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda; all equal to expected"
- coverage: "4 of 4 hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0003
- type: "check-card"
- doubt: "Was layout.indd moved or renamed inside the project?"
- decision: "whether layout.indd is moved in scope or needs a copy"
- operation: "D6 file-agent under the project, exact size 16384, depth 8"
- outcomes: "candidates: hash them; empty and complete: not relocated in scope"
- cost: "one size-filtered listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0007
- type: "observation"
- check_card: "CHK-0002-0003"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "no file of 16384 bytes; unreadable subfolder /data/studio/projects/aurora/raw"
- coverage: "not truncated, possibly incomplete: raw unreadable"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0004
- type: "check-card"
- doubt: "Which subfolders of the project can be searched separately?"
- decision: "how to complete the in-scope search for layout.indd"
- operation: "D13 file-agent on the project"
- outcomes: "subfolders to repeat the size search in"
- cost: "one listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0008
- type: "observation"
- check_card: "CHK-0002-0004"
- agent: "file-agent"
- delegation: "D13"
- state: "completed"
- result: "subfolders /data/studio/projects/aurora/exports and /data/studio/projects/aurora/raw"
- coverage: "not truncated, none unreadable"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0005
- type: "check-card"
- doubt: "Is layout.indd inside raw/?"
- decision: "whether the relocation hypothesis can be closed"
- operation: "D6 file-agent under raw, exact size 16384, depth 8"
- outcomes: "candidates: hash them; empty and complete: not relocated in scope"
- cost: "one size-filtered listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0009
- type: "observation"
- check_card: "CHK-0002-0005"
- agent: "file-agent"
- delegation: "D6"
- state: "failed"
- result: "permission_denied"
- coverage: "raw/ not reviewed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0006
- type: "check-card"
- doubt: "Can the real path of backups/aurora-2026-10-01 be resolved?"
- decision: "whether recorded copy CPY-0001-0015 of layout.indd may be checked and used"
- operation: "D2 file-agent on /data/studio/backups/aurora-2026-10-01"
- outcomes: "real path: check CPY-0001-0015 with D5 and D7; none: copy not read"
- cost: "one metadata query, read-only"
- budget_left: 296

## RECORD OBS-0002-0010
- type: "observation"
- check_card: "CHK-0002-0006"
- agent: "file-agent"
- delegation: "D2"
- state: "completed"
- result: "/data/studio/backups/aurora-2026-10-01 exists and readable, no real path returned (second time)"
- coverage: "1 of 1 folder, real path missing"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0007
- type: "check-card"
- doubt: "Is there an unrecorded copy of layout.indd version VER-0001-0006 in backups/aurora-2026-11-05?"
- decision: "source for layout.indd"
- operation: "D6 file-agent, exact size 16384, depth 8"
- outcomes: "candidates: hash them; empty and complete: no copy there"
- cost: "one size-filtered listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0011
- type: "observation"
- check_card: "CHK-0002-0007"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "no file of 16384 bytes under /data/studio/backups/aurora-2026-11-05"
- coverage: "not truncated, no unreadable subfolder, complete to depth 8"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0002-0008
- type: "check-card"
- doubt: "Is there an unrecorded copy of layout.indd version VER-0001-0006 in usb-archive/aurora?"
- decision: "source for layout.indd"
- operation: "D6 file-agent, exact size 16384, depth 8"
- outcomes: "candidates: hash them; empty and complete: no copy there"
- cost: "one size-filtered listing, read-only"
- budget_left: 296

## RECORD OBS-0002-0012
- type: "observation"
- check_card: "CHK-0002-0008"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "no file of 16384 bytes under /data/studio/usb-archive/aurora"
- coverage: "not truncated, no unreadable subfolder, complete to depth 8"
- observed_at: "unknown"
- class: "observed"