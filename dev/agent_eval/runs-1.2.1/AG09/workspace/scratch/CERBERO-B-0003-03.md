# CERBERO BUNDLE B-0003-03
- schema: "cerbero-memory-2"
- bundle_id: "B-0003-03"
- case_id: "CAS-0003"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD OBS-0003-0019
- type: "observation"
- check_card: null
- agent: "document-agent"
- delegation: "D8"
- state: "completed"
- result: "{\"format\": \"pdf\", \"path\": \"recovered/cerbero-rebuild-CAS-0003/brief.pdf\", \"read\": \"whole file\", \"realpath\": \"recovered/cerbero-rebuild-CAS-0003/brief.pdf\"}"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0020
- type: "observation"
- check_card: null
- agent: "document-agent"
- delegation: "D8"
- state: "completed"
- result: "{\"format\": \"docx\", \"path\": \"recovered/cerbero-rebuild-CAS-0003/copy.docx\", \"read\": \"whole file\", \"realpath\": \"recovered/cerbero-rebuild-CAS-0003/copy.docx\"}"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0021
- type: "observation"
- check_card: null
- agent: "document-agent"
- delegation: "D8"
- state: "failed"
- result: "{\"code\": \"not_supported\", \"path\": \"recovered/cerbero-rebuild-CAS-0003/cover.tif\"}"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0022
- type: "observation"
- check_card: null
- agent: "document-agent"
- delegation: "D8"
- state: "failed"
- result: "{\"code\": \"not_supported\", \"path\": \"recovered/cerbero-rebuild-CAS-0003/layout.indd\"}"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0023
- type: "observation"
- check_card: null
- agent: "document-agent"
- delegation: "D8"
- state: "failed"
- result: "{\"code\": \"not_supported\", \"path\": \"recovered/cerbero-rebuild-CAS-0003/logo.ai\"}"
- coverage: "as returned"
- observed_at: "unknown"
- class: "observed"

## RECORD APR-0003-01
- type: "approval"
- plan_id: "PLN-0003-01"
- plan_sha256: "b63cb19f09669bb066ef1b1395af5ed5a84a59ec2499934152332c160331afc5"
- decision: "granted"
- statement: "user reply in session"

## RECORD RCP-0003-01
- type: "receipt"
- plan_id: "PLN-0003-01"
- plan_sha256: "b63cb19f09669bb066ef1b1395af5ed5a84a59ec2499934152332c160331afc5"
- overall: "verified"
- reference: "approved-version"
- set_complete: true
- coverage: "see case records"
- reason: null
- pending: []
- outside_target: []

## RECORD REN-0003-01-01
- type: "receipt-entry"
- receipt_id: "RCP-0003-01"
- entry_id: "ENT-0003-01-01"
- asset_id: "AST-0001-0001"
- version_id: "VER-0001-0001"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/brief.pdf"
- source_sha256_before: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- destination_sha256: "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512"
- source_sha256_after: null
- note: ""
- name: "brief.pdf"
- source_path: "/data/studio/projects/aurora/brief-FINAL.pdf"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0001", "format": "opened by document-agent (pdf, whole file)", "provenance": "original in the project folder, moved to projects/aurora/brief-FINAL.pdf"}

## RECORD REN-0003-01-02
- type: "receipt-entry"
- receipt_id: "RCP-0003-01"
- entry_id: "ENT-0003-01-02"
- asset_id: "AST-0001-0002"
- version_id: "VER-0001-0002"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/copy.docx"
- source_sha256_before: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- destination_sha256: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- source_sha256_after: null
- note: ""
- name: "copy.docx"
- source_path: "/data/studio/backups/aurora-2026-10-01/copy.docx"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0002", "format": "opened by document-agent (docx, whole file)", "provenance": "copy in backups/aurora-2026-10-01"}

## RECORD REN-0003-01-03
- type: "receipt-entry"
- receipt_id: "RCP-0003-01"
- entry_id: "ENT-0003-01-03"
- asset_id: "AST-0001-0003"
- version_id: "VER-0001-0003"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/cover.tif"
- source_sha256_before: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- destination_sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- source_sha256_after: null
- note: ""
- name: "cover.tif"
- source_path: "/data/studio/backups/aurora-2026-10-01/cover.tif"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0003", "format": "not available: no registered expert opens .tif files", "provenance": "copy in backups/aurora-2026-10-01"}

## RECORD REN-0003-01-04
- type: "receipt-entry"
- receipt_id: "RCP-0003-01"
- entry_id: "ENT-0003-01-04"
- asset_id: "AST-0001-0006"
- version_id: "VER-0001-0006"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/layout.indd"
- source_sha256_before: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- destination_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- source_sha256_after: null
- note: ""
- name: "layout.indd"
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0006", "format": "not available: no registered expert opens .indd files", "provenance": "copy in backups/aurora-2026-10-01"}

## RECORD REN-0003-01-05
- type: "receipt-entry"
- receipt_id: "RCP-0003-01"
- entry_id: "ENT-0003-01-05"
- asset_id: "AST-0001-0007"
- version_id: "VER-0001-0007"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-rebuild-CAS-0003/logo.ai"
- source_sha256_before: "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"
- destination_sha256: "1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda"
- source_sha256_after: null
- note: ""
- name: "logo.ai"
- source_path: "/data/studio/projects/aurora/logo.ai"
- checks: {"bytes": "equal to the source digest observed before copying", "version": "equal to approved version VER-0001-0007", "format": "not available: no registered expert opens .ai files", "provenance": "original in the project folder"}
