# CERBERO BUNDLE B-0002-03
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-03"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD APR-0002-01
- type: "approval"
- plan_id: "PLN-0002-01"
- plan_sha256: "314b262e1dc95aa3fea53a37bb2a8f266278c7e9b4a39c0f8e968281bf04c754"
- decision: "granted"
- statement: "user reply in session"

## RECORD RCP-0002-01
- type: "receipt"
- plan_id: "PLN-0002-01"
- plan_sha256: "314b262e1dc95aa3fea53a37bb2a8f266278c7e9b4a39c0f8e968281bf04c754"
- overall: "verified"
- reference: "approved-version"
- set_complete: true
- coverage: "see case records"
- reason: null
- pending: []
- outside_target: ["AST-0001-0010"]

## RECORD REN-0002-01-01
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: "ENT-0002-01-01"
- asset_id: "AST-0001-0002"
- version_id: "VER-0001-0002"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/copy.docx"
- source_sha256_before: "0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"
- destination_sha256: "0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4"
- source_sha256_after: null
- note: ""
- name: "copy.docx"
- source_path: "/data/studio/backups/aurora-2026-10-01/copy.docx"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0002", "format": "not checked", "provenance": "copy in backups/aurora-2026-10-01"}

## RECORD REN-0002-01-02
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: "ENT-0002-01-02"
- asset_id: "AST-0001-0003"
- version_id: "VER-0001-0003"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/cover.tif"
- source_sha256_before: "2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"
- destination_sha256: "2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef"
- source_sha256_after: null
- note: ""
- name: "cover.tif"
- source_path: "/data/studio/backups/aurora-2026-10-01/cover.tif"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0003", "format": "not checked", "provenance": "copy in backups/aurora-2026-10-01"}

## RECORD REN-0002-01-03
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: "ENT-0002-01-03"
- asset_id: "AST-0001-0006"
- version_id: "VER-0001-0006"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd"
- source_sha256_before: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- destination_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- source_sha256_after: null
- note: ""
- name: "layout.indd"
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0006", "format": "not checked", "provenance": "copy in backups/aurora-2026-10-01"}
