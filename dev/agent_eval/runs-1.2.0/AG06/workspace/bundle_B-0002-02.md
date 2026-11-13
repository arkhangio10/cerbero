# CERBERO BUNDLE B-0002-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-02"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CLM-0002-0001
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0001"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/brief.pdf"
- statement: "brief.pdf holds Delivery 2 version VER-0001-0001"
- class: "observed"
- supports: ["OBS-0002-0005", "OBS-0002-0006"]
- contradicts: []
- depends_on: ["VER-0001-0001", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0002
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0002"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/copy.docx"
- statement: "copy.docx holds Delivery 2 version VER-0001-0002"
- class: "observed"
- supports: ["OBS-0002-0005", "OBS-0002-0006"]
- contradicts: []
- depends_on: ["VER-0001-0002", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0003
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0003"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/cover.tif"
- statement: "cover.tif holds Delivery 2 version VER-0001-0003"
- class: "observed"
- supports: ["OBS-0002-0005", "OBS-0002-0006"]
- contradicts: []
- depends_on: ["VER-0001-0003", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0004
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0007"
- asset_state: "intact"
- located_at: "/data/studio/projects/aurora/logo.ai"
- statement: "logo.ai holds Delivery 2 version VER-0001-0007"
- class: "observed"
- supports: ["OBS-0002-0005", "OBS-0002-0006"]
- contradicts: []
- depends_on: ["VER-0001-0007", "OBS-0002-0006"]
- status: "current"

## RECORD CLM-0002-0005
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0006"
- asset_state: "missing"
- located_at: null
- statement: "layout.indd is missing at /data/studio/projects/aurora/layout.indd; in-scope search incomplete because raw/ is unreadable; cause unknown"
- class: "observed"
- supports: ["OBS-0002-0005", "OBS-0002-0007", "OBS-0002-0009"]
- contradicts: []
- depends_on: ["OBS-0002-0005", "OBS-0002-0007"]
- status: "current"

## RECORD CLM-0002-0006
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0004"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/exports/previews/cover-preview.jpg"
- statement: "same size and time as recorded; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0007
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0005"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/fonts-license.pdf"
- statement: "same size and time as recorded; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0008
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0008"
- asset_state: "intact-metadata"
- located_at: "/data/studio/projects/aurora/palette.ase"
- statement: "same size and time as recorded; content not hashed"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0009
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0009"
- asset_state: "unknown"
- located_at: null
- statement: "raw/DSC_0101.ARW permission_denied; state unknown"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0010
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0010"
- asset_state: "unknown"
- located_at: null
- statement: "raw/DSC_0142.ARW permission_denied; state unknown"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0011
- type: "claim"
- kind: "asset-state"
- subject: "AST-0001-0011"
- asset_state: "unknown"
- located_at: null
- statement: "raw/DSC_0150.ARW permission_denied; state unknown"
- class: "observed"
- supports: ["OBS-0002-0005"]
- contradicts: []
- depends_on: ["OBS-0002-0005"]
- status: "current"

## RECORD CLM-0002-0012
- type: "claim"
- kind: "contradiction"
- subject: "CPY-0001-0006"
- statement: "copy record CPY-0001-0006 holds VER-0001-0006 at /data/studio/projects/aurora/layout.indd (OBS-0001-0006); D5 now reports that path not_found (OBS-0002-0005)"
- class: "contradicted"
- supports: ["OBS-0002-0005"]
- contradicts: ["CPY-0001-0006", "OBS-0001-0006"]
- depends_on: ["CPY-0001-0006", "OBS-0002-0005"]
- status: "current"

## RECORD CPY-0002-0001
- type: "copy"
- version_id: "VER-0001-0006"
- real_path: "/data/studio/projects/aurora/layout.indd"
- location_id: "LOC-0001-0001"
- sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- observation: "OBS-0002-0005"
- access: "unknown"
- status: "needs-review"
- supersedes: "CPY-0001-0006"

## RECORD HYP-0002-0001
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd was moved or renamed inside the project"
- status: "open"
- for: []
- against: ["OBS-0002-0007"]
- next_check: "D6 exact size 16384 under raw/ once it is readable, then D7 on candidates"

## RECORD HYP-0002-0002
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent with a copy of VER-0001-0006 elsewhere"
- status: "undetermined"
- for: ["CPY-0001-0015"]
- against: ["OBS-0002-0011", "OBS-0002-0012"]
- next_check: "D2 returns a real path for /data/studio/backups/aurora-2026-10-01; then D5 and D7 on CPY-0001-0015"

## RECORD HYP-0002-0003
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd is absent without any copy in the named locations"
- status: "open"
- for: ["OBS-0002-0011", "OBS-0002-0012"]
- against: ["CPY-0001-0015"]
- next_check: "same as HYP-0002-0002"

## RECORD HYP-0002-0004
- type: "hypothesis"
- subject: "AST-0001-0006"
- text: "layout.indd exists but is not visible to Cerbero, for example inside raw/"
- status: "open"
- for: ["OBS-0002-0009"]
- against: []
- next_check: "read access to raw/ granted by an administrator, then D6 and D7"

## RECORD OPN-0002-0001
- type: "open-item"
- subject: "/data/studio/backups/aurora-2026-10-01"
- reason: "D2 returned no real path twice; containment unknown; recorded copy CPY-0001-0015 of layout.indd VER-0001-0006 not read"
- needed_to_resolve: "the NAS reports a real path for that folder"

## RECORD OPN-0002-0002
- type: "open-item"
- subject: "/data/studio/projects/aurora/raw"
- reason: "permission_denied on D5 and D6; DSC_0101.ARW, DSC_0142.ARW, DSC_0150.ARW unknown; layout.indd relocation search incomplete there"
- needed_to_resolve: "read access to raw/"

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/data/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "recover approved set SET-0001-0002 (Delivery 2) member layout.indd, version VER-0001-0006; partial recovery chosen by the user (STM-0002-0002); no entry can be executed, so no folder is created and nothing is copied"
- preconditions: "none executable: layout.indd has no source whose real path could be checked in scope"
- success_conditions: "not applicable: plan has no entries"
- risks: "layout.indd remains missing; the only recorded copy lies in a folder whose real path was not returned"
- pending: ["layout.indd"]
- previous_receipt: null
- supersedes_plan: null
- target_kind: "approved-set"
- target_members: ["AST-0001-0001", "AST-0001-0006", "AST-0001-0002", "AST-0001-0003", "AST-0001-0007"]
- outside_target: []

## RECORD APR-0002-0001
- type: "approval"
- plan_id: "PLN-0002-01"
- plan_sha256: null
- decision: "not-requested"
- statement: "the plan has no executable entry; no plan confirmation was asked"

## RECORD RCP-0002-01
- type: "receipt"
- plan_id: "PLN-0002-01"
- plan_sha256: null
- overall: "failed"
- reference: "approved-version"
- set_complete: false
- coverage: "11 recorded assets by metadata; 4 of 5 Delivery 2 members hashed equal; raw/ unreadable; backups/aurora-2026-11-05 and usb-archive/aurora complete to depth 8 for size 16384; backups/aurora-2026-10-01 not read (no real path)"
- pending: ["layout.indd"]
- reason: "the target needed a copy of layout.indd VER-0001-0006 and none could be planned: no eligible source could be checked"
- outside_target: []

## RECORD REN-0002-01-01
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: null
- asset_id: "AST-0001-0006"
- version_id: "VER-0001-0006"
- status: "no-source"
- destination_path: null
- source_sha256_before: null
- destination_sha256: null
- source_sha256_after: null
- note: "missing in the project; no size match in backups/aurora-2026-11-05 or usb-archive/aurora; recorded copy CPY-0001-0015 in backups/aurora-2026-10-01 not read because the NAS returned no real path for that folder"
- name: "layout.indd"
- source_path: null
- checks: {"bytes": "not-run", "version": "not-run", "format": "not-run"}
