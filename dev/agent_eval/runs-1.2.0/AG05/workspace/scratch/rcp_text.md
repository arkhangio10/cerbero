# CERBERO BUNDLE B-0001-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0001-02"
- case_id: "CAS-0001"
- scope_id: null
- supersedes: null

## RECORD OBS-0001-0006
- type: "observation"
- check_card: null
- agent: "knowledge-agent"
- delegation: "D10"
- state: "completed"
- result: "plan bundle B-0001-01 saved at /data/studio/cerbero-memory/CERBERO-B-0001-01.md, verified true, 6405 bytes saved of 6405 sent; NAS approval APV-1 granted by the user"
- coverage: "1 of 1 save persisted"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0007
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 6ac15ae8f29cad99476476ff625380f3bacf351d5f4206c58f14ccd9a07e95b7, 6405 bytes, same real path"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD STM-0001-0003
- type: "statement"
- text: "Yes. I confirm the approved set you showed and I approve plan PLN-0001-01 with that digest."
- given_in: "CAS-0001 answer to the confirmation of plan PLN-0001-01 with digest 6ac15ae8f29cad99476476ff625380f3bacf351d5f4206c58f14ccd9a07e95b7"
- class: "user-declared"

## RECORD APR-0001-01
- type: "approval"
- plan_id: "PLN-0001-01"
- plan_sha256: "6ac15ae8f29cad99476476ff625380f3bacf351d5f4206c58f14ccd9a07e95b7"
- decision: "granted"
- statement: "Yes. I confirm the approved set you showed and I approve plan PLN-0001-01 with that digest. (STM-0001-0003; the plan had no approved set: target chosen-files, member layout.indd, reference source-fidelity)"

## RECORD OBS-0001-0008
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "re-check before the first change: /data/studio/cerbero-memory/CERBERO-B-0001-01.md sha256 6ac15ae8f29cad99476476ff625380f3bacf351d5f4206c58f14ccd9a07e95b7, 6405 bytes, matches the confirmed digest"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0009
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D11"
- state: "completed"
- result: "created /data/studio/recovered/cerbero-recovery-CAS-0001, equal to the planned path; no subfolders requested; NAS approval APV-2 granted by the user"
- coverage: "1 of 1 folder created"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0010
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "/data/studio/recovered/cerbero-recovery-CAS-0001/layout.indd does not exist (not_found) before the copy"
- coverage: "1 of 1 paths reported"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0011
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "source before copy: /data/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes, same real path, matches the expected digest"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0012
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D12"
- state: "completed"
- result: "copied; real destination path /data/studio/recovered/cerbero-recovery-CAS-0001/layout.indd, equal to the planned path; NAS approval APV-3 granted by the user"
- coverage: "1 of 1 copies"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0001-0013
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "destination: /data/studio/recovered/cerbero-recovery-CAS-0001/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes, same real path, matches the expected digest"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD RCP-0001-01
- type: "receipt"
- plan_id: "PLN-0001-01"
- plan_sha256: "6ac15ae8f29cad99476476ff625380f3bacf351d5f4206c58f14ccd9a07e95b7"
- overall: "fidelity-only"
- reference: "source-fidelity"
- set_complete: null
- coverage: "target chosen-files: 1 of 1 member planned, copied and checked; source hashed 2 times, destination 1 time, plan file 2 times; memory listing complete with 0 files at load; no project folder named, no listing of the source location, failure domains unknown"
- pending: []
- reason: "no prior reference: the copy equals the source chosen by the user; whether that source is the version the user expects could not be checked against any earlier reference"
- outside_target: []

## RECORD REN-0001-01-01
- type: "receipt-entry"
- receipt_id: "RCP-0001-01"
- entry_id: "ENT-0001-01-01"
- asset_id: null
- version_id: null
- status: "fidelity-only"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0001/layout.indd"
- source_sha256_before: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- destination_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- source_sha256_after: null
- note: "destination digest equals the source digest observed just before the copy (OBS-0001-0011, OBS-0001-0013); source not re-hashed after the copy because the digests matched"
- name: "layout.indd"
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- checks: {"bytes": "equal to source", "version": "not checkable: no approved version recorded", "format": "not run: this was not a rebuild, and no registered expert opens .indd files", "provenance": "copy at /data/studio/backups/aurora-2026-10-01"}
