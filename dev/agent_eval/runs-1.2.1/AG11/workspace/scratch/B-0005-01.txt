# CERBERO BUNDLE B-0005-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0005-01"
- case_id: "CAS-0005"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0005
- type: "case"
- scope_id: "SCP-0001"
- request: "what-if: which files could be lost if the volume that holds project Aurora failed"
- status: "open"
- opened_in: "this session"

## RECORD STM-0005-0001
- type: "statement"
- text: "Review project Aurora: which files could I lose if the volume that holds the project failed? Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora."
- given_in: "this session, the request"
- class: "user-declared"

## RECORD OBS-0005-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D1, D2"
- state: "completed"
- result: "user folder /data/studio; the five named folders exist, are readable and have real paths equal to the names given: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora"
- coverage: "5 of 5 named folders resolved"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0005-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3, D4, D7"
- state: "completed"
- result: "D3 listed 16 CERBERO- files, not truncated; newest index IDX-0004-01 read in full (3641 bytes, digest 0a1b51c1110dc8e875a6ac118380e812985673c13bfe665e8e41665c04f692b6); B-0001-01, B-0001-02, B-0002-01, B-0002-02, B-0002-03, B-0003-01, B-0003-02, B-0004-01, B-0004-02, TD-0000-01 and TH-0000-02 read in full with byte counts equal to the listing, and their 11 digests equal the index digests; 167 records parsed and valid, every reference resolved"
- coverage: "12 of 16 memory files hashed and read; IDX-0001-01, IDX-0002-01, IDX-0003-01 (superseded) and TH-0000-01 (holdout file of rejected POL-0003-0002) not read or hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0005-0001
- type: "check-card"
- doubt: "Which files does the project folder hold now, and which files are in raw?"
- decision: "which files a Volume 1 failure would reach, and which raw files active policy POL-0004-0003 v2 requires digesting"
- operation: "D6 file-agent on /data/studio/projects/aurora, of any size, limit 200, depth 8"
- outcomes: "complete listing: current files and raw files known; possibly incomplete: split with D13; recorded path absent: contradiction with its project copy record; unrecorded file: no recorded copy"
- cost: "1 listing, read-only"
- budget_left: 300

## RECORD OBS-0005-0003
- type: "observation"
- check_card: "CHK-0005-0001"
- agent: "file-agent"
- delegation: "D6"
- state: "completed"
- result: "9 files under /data/studio/projects/aurora: brief-FINAL.pdf 4096 bytes mtime 1100; cover.tif 32768 mtime 1103; exports/previews/cover-preview.jpg 4096 mtime 1104; fonts-license.pdf 2048 mtime 900; logo.ai 8192 mtime 900; notes/README-RECOVERY.txt 237 mtime 2000; palette.ase 512 mtime 900; raw/DSC_0101.ARW 65536 mtime 800; raw/DSC_0150.ARW 65536 mtime 802. Not listed: the recorded paths brief.pdf, copy.docx, layout.indd and raw/DSC_0142.ARW"
- coverage: "complete to depth 8: 9 entries, below the limit of 200, truncated false, no unreadable subfolder"
- observed_at: "unknown"
- class: "observed"

## RECORD CHK-0005-0002
- type: "check-card"
- doubt: "Do raw/DSC_0101.ARW and raw/DSC_0150.ARW still hold VER-0001-0009 and VER-0001-0011?"
- decision: "which raw versions the Volume 1 map evaluates; run because active policy POL-0004-0003 v2 (promote-critical raw, frozen digest cb236cf7ff4380c8fa2933ce885eed9c083123c479bb4bb688b2dcc650aa7032, evaluation EVL-0004-0001, approval STM-0004-0003) passed the activation checks in this session"
- operation: "D7 file-agent"
- outcomes: "equal digest: intact and mapped; different digest: altered, its current content has no recorded copy"
- cost: "2 digests, 131072 bytes, read-only"
- budget_left: 300

## RECORD OBS-0005-0004
- type: "observation"
- check_card: "CHK-0005-0002"
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/projects/aurora/raw/DSC_0101.ARW digest 2cca9c67186306e2378e0aae5ef4c7b8306eee635c7343e3fd8a500679cb5442, 65536 bytes, matches VER-0001-0009; /data/studio/projects/aurora/raw/DSC_0150.ARW digest 88e99368f265eba2034cc29141ca1f3e738cf2c93abfd29e4404dc6ec07a6004, 65536 bytes, matches VER-0001-0011"
- coverage: "2 of 2 raw files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0005-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "intact"
- located_at: null
- statement: "raw/DSC_0101.ARW is intact relative to VER-0001-0009"
- supports: ["OBS-0005-0004"]
- contradicts: []
- depends_on: ["VER-0001-0009", "OBS-0005-0004"]
- status: "current"
- class: "observed"

## RECORD CLM-0005-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "intact"
- located_at: null
- statement: "raw/DSC_0150.ARW is intact relative to VER-0001-0011"
- supports: ["OBS-0005-0004"]
- contradicts: []
- depends_on: ["VER-0001-0011", "OBS-0005-0004"]
- status: "current"
- class: "observed"

## RECORD CLM-0005-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: null
- statement: "exports/previews/cover-preview.jpg has the recorded size and modification time of VER-0001-0004; content not hashed"
- supports: ["OBS-0005-0003"]
- contradicts: []
- depends_on: ["VER-0001-0004", "OBS-0005-0003"]
- status: "current"
- class: "observed"

## RECORD CLM-0005-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: null
- statement: "fonts-license.pdf has the recorded size and modification time of VER-0001-0005; content not hashed"
- supports: ["OBS-0005-0003"]
- contradicts: []
- depends_on: ["VER-0001-0005", "OBS-0005-0003"]
- status: "current"
- class: "observed"

## RECORD CLM-0005-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: null
- statement: "palette.ase has the recorded size and modification time of VER-0001-0008; content not hashed"
- supports: ["OBS-0005-0003"]
- contradicts: []
- depends_on: ["VER-0001-0008", "OBS-0005-0003"]
- status: "current"
- class: "observed"

## RECORD CLM-0005-0006
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0001"
- statement: "copy record CPY-0001-0001 places VER-0001-0001 at /data/studio/projects/aurora/brief.pdf; the D6 listing of this session does not list that path; CAS-0002 found this version at brief-FINAL.pdf (CLM-0002-0008)"
- supports: ["OBS-0005-0003"]
- contradicts: ["CPY-0001-0001"]
- depends_on: ["CPY-0001-0001", "OBS-0005-0003"]
- status: "current"
- class: "contradicted"

## RECORD CLM-0005-0007
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0002"
- statement: "copy record CPY-0001-0002 places VER-0001-0002 at /data/studio/projects/aurora/copy.docx; the D6 listing of this session does not list that path (also absent in CAS-0002, CLM-0002-0009)"
- supports: ["OBS-0005-0003"]
- contradicts: ["CPY-0001-0002"]
- depends_on: ["CPY-0001-0002", "OBS-0005-0003"]
- status: "current"
- class: "contradicted"

## RECORD CLM-0005-0008
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "copy record CPY-0001-0006 places VER-0001-0006 at /data/studio/projects/aurora/layout.indd; the D6 listing of this session does not list that path (also absent in CAS-0002, CLM-0002-0010)"
- supports: ["OBS-0005-0003"]
- contradicts: ["CPY-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0005-0003"]
- status: "current"
- class: "contradicted"

## RECORD CLM-0005-0009
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0010"
- statement: "copy record CPY-0001-0010 places VER-0001-0010 at /data/studio/projects/aurora/raw/DSC_0142.ARW; the D6 listing of this session does not list that path (also absent in CAS-0002, CLM-0002-0011)"
- supports: ["OBS-0005-0003"]
- contradicts: ["CPY-0001-0010"]
- depends_on: ["CPY-0001-0010", "OBS-0005-0003"]
- status: "current"
- class: "contradicted"

## RECORD CLM-0005-0010
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0003"
- statement: "copy record CPY-0001-0003 places VER-0001-0003 at /data/studio/projects/aurora/cover.tif; CAS-0002 observed digest 93bffe5d03dc8c751aec64a596713512cdb2369b4227d2bc4412a45c01867275 at that path (CLM-0002-0001); the copy record was not revalidated then"
- supports: ["OBS-0002-0004"]
- contradicts: ["CPY-0001-0003"]
- depends_on: ["CPY-0001-0003", "OBS-0002-0004"]
- status: "current"
- class: "contradicted"

## RECORD CPY-0005-0001
- type: "copy"
- version_id: "VER-0001-0001"
- real_path: "/data/studio/projects/aurora/brief.pdf"
- location_id: "LOC-0001-0001"
- sha256: "9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0001"

## RECORD CPY-0005-0002
- type: "copy"
- version_id: "VER-0001-0002"
- real_path: "/data/studio/projects/aurora/copy.docx"
- location_id: "LOC-0001-0001"
- sha256: "0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0002"

## RECORD CPY-0005-0003
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD CPY-0005-0004
- type: "copy"
- version_id: "VER-0001-0010"
- real_path: "/data/studio/projects/aurora/raw/DSC_0142.ARW"
- location_id: "LOC-0001-0001"
- sha256: "2653339b90e2c2b0bd1cb1abbf34d1bbabb08e3ece0c62710a8d4ea177f4fe1a"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0010"

## RECORD CPY-0005-0005
- type: "copy"
- version_id: "VER-0001-0003"
- real_path: "/data/studio/projects/aurora/cover.tif"
- location_id: "LOC-0001-0001"
- sha256: "2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"
- observation: "OBS-0001-0006"
- access: "readable"
- status: "needs-review"
- supersedes: "CPY-0001-0003"

## RECORD CLM-0005-0011
- type: "claim"
- kind: "recoverability"
- subject: "LOC-0001-0004"
- statement: "Under a failure of Volume 1 (DOM-0001-0001, recorded on device DOM-0001-0003 this NAS), /data/studio/usb-archive/aurora is outside the failure because it is recorded on a different device, DOM-0001-0004 external USB drive; its volume is unknown"
- supports: ["STM-0001-0003"]
- contradicts: []
- depends_on: ["STM-0001-0003", "DOM-0001-0001", "DOM-0001-0003", "DOM-0001-0004", "LOC-0001-0004"]
- status: "current"
- class: "inferred"

## RECORD MAP-0005-0001
- type: "map"
- subject: "SET-0001-0002"
- scenario: "domain failure of volume DOM-0001-0001 (Volume 1, recorded for the project location LOC-0001-0001)"
- verdict: "recoverable"
- members: {"VER-0001-0001": "brief.pdf: 1 eligible (CPY-0001-0012 backups/aurora-2026-10-01), 0 uncertain, modeled", "VER-0001-0006": "layout.indd: 1 eligible (CPY-0001-0015 backups/aurora-2026-10-01), 0 uncertain, modeled", "VER-0001-0002": "copy.docx: 2 eligible (CPY-0001-0013, CPY-0001-0017 on Volume 2), 0 uncertain, modeled", "VER-0001-0003": "cover.tif: 2 eligible (CPY-0001-0014, CPY-0001-0018 on Volume 2), 0 uncertain, modeled", "VER-0001-0007": "logo.ai: 2 eligible (CPY-0001-0016 on Volume 2, CPY-0001-0023 usb-archive by CLM-0005-0011), 0 uncertain, modeled"}
- evidence_level: "modeled"
- unknowns: ["storage pool and site of all four locations unknown (STM-0001-0003); volume of usb-archive/aurora unknown", "copies outside the project not re-observed in this session: recorded by the CAS-0001 Baseline, time unknown", "both backup folders are on Volume 2 of the same NAS: brief.pdf and layout.indd rely on one copy each"]

## RECORD MAP-0005-0002
- type: "map"
- subject: "SET-0001-0001"
- scenario: "domain failure of volume DOM-0001-0001 (Volume 1, recorded for the project location LOC-0001-0001)"
- verdict: "recoverable"
- members: {"VER-0001-0012": "brief.pdf: 1 eligible (CPY-0001-0019 usb-archive by CLM-0005-0011), 0 uncertain, modeled", "VER-0001-0013": "layout.indd: 1 eligible (CPY-0001-0022 usb-archive by CLM-0005-0011), 0 uncertain, modeled", "VER-0001-0014": "copy.docx: 1 eligible (CPY-0001-0020 usb-archive by CLM-0005-0011), 0 uncertain, modeled", "VER-0001-0015": "cover.tif: 1 eligible (CPY-0001-0021 usb-archive by CLM-0005-0011), 0 uncertain, modeled", "VER-0001-0007": "logo.ai: 2 eligible (CPY-0001-0016 on Volume 2, CPY-0001-0023 usb-archive), 0 uncertain, modeled"}
- evidence_level: "modeled"
- unknowns: ["storage pool and site of all four locations unknown (STM-0001-0003); volume of usb-archive/aurora unknown", "copies outside the project not re-observed in this session: recorded by the CAS-0001 Baseline, time unknown", "four of five members rely only on the USB archive, whose exclusion from the failure is an inference (CLM-0005-0011)"]

## RECORD MAP-0005-0003
- type: "map"
- subject: "SCP-0001"
- scenario: "domain failure of volume DOM-0001-0001 (Volume 1, recorded for the project location LOC-0001-0001); recorded versions outside the approved sets, raw included by policy POL-0004-0003 v2"
- verdict: "not-recoverable"
- members: {"VER-0001-0009": "raw/DSC_0101.ARW: 0 eligible, 0 uncertain, none: only copy CPY-0001-0009 in the project, digest verified now (OBS-0005-0004); at risk", "VER-0001-0011": "raw/DSC_0150.ARW: 0 eligible, 0 uncertain, none: only copy CPY-0001-0011 in the project, digest verified now (OBS-0005-0004); at risk", "VER-0001-0004": "exports/previews/cover-preview.jpg: 0 eligible, 0 uncertain, none: only copy CPY-0001-0004 in the project; no user statement declares the folder regenerable", "VER-0001-0005": "fonts-license.pdf: 0 eligible, 0 uncertain, none: only copy CPY-0001-0005 in the project", "VER-0001-0008": "palette.ase: 0 eligible, 0 uncertain, none: only copy CPY-0001-0008 in the project", "VER-0001-0010": "raw/DSC_0142.ARW: already missing since CAS-0002 (CLM-0002-0011, CLM-0005-0009); no copy in the named locations"}
- evidence_level: "none"
- unknowns: ["storage pool and site of all four locations unknown (STM-0001-0003); volume of usb-archive/aurora unknown", "copies outside the project not re-observed in this session: recorded by the CAS-0001 Baseline, time unknown", "inventories of the three copy locations are recorded complete at Baseline, depth not recorded; copies added there since are not known", "not recorded as versions, so no copy is known: notes/README-RECOVERY.txt (237 bytes) and the current content of cover.tif (digest 93bf...7275, OBS-0002-0004)"]

## RECORD OPN-0005-0001
- type: "open-item"
- subject: "failure domains of the four locations"
- reason: "storage pool and site never stated for any location, and the volume of /data/studio/usb-archive/aurora is unknown (STM-0001-0003); storage-pool, device and site failures were not evaluated"
- needed_to_resolve: "a user statement of those domains"

## RECORD OPN-0005-0002
- type: "open-item"
- subject: "copies outside Volume 1"
- reason: "the maps MAP-0005-0001 to MAP-0005-0003 are modeled from Baseline observations; no copy outside the project was re-observed in this session"
- needed_to_resolve: "a user request to verify the copies now with D5 and D7, read-only"
