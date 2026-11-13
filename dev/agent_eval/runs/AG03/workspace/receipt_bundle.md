# CERBERO BUNDLE B-0002-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-02"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD OBS-0002-0013
- type: "observation"
- check_card: null
- agent: "knowledge-agent"
- delegation: "D10"
- state: "completed"
- result: "plan bundle B-0002-01 saved at /data/studio/cerbero-memory/CERBERO-B-0002-01.md, verified true, 20258 bytes; NAS approval APV-1 answered by the user: granted"
- coverage: "1 of 1 saves"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0014
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "/data/studio/cerbero-memory/CERBERO-B-0002-01.md sha256 bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569, 20258 bytes"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0015
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "plan file re-hashed immediately before the first change: sha256 bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569, matches the confirmed digest"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0016
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D11"
- state: "completed"
- result: "created /data/studio/recovered/cerbero-recovery-CAS-0002 (no subfolders); NAS approval APV-2 answered by the user: granted"
- coverage: "1 of 1 folders"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0017
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D5"
- state: "completed"
- result: "/data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd does not exist (reason not_found)"
- coverage: "1 of 1 paths"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0018
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "source /data/studio/backups/aurora-2026-10-01/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes, matches expected, immediately before copying"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0019
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D12"
- state: "completed"
- result: "copied /data/studio/backups/aurora-2026-10-01/layout.indd; real destination path /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd; NAS result copied; NAS approval APV-3 answered by the user: granted"
- coverage: "1 of 1 copies"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0002-0020
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "destination /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd sha256 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b, 16384 bytes, matches expected"
- coverage: "1 of 1 files hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD APR-0002-01
- type: "approval"
- plan_id: "PLN-0002-01"
- plan_sha256: "bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569"
- decision: "granted"
- statement: "Yes. I confirm the approved set you showed and I approve plan PLN-0002-01 with that digest."

## RECORD RCP-0002-01
- type: "receipt"
- plan_id: "PLN-0002-01"
- plan_sha256: "bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569"
- overall: "partial"
- reference: "approved-version"
- set_complete: false
- coverage: "1 plan entry executed and verified by digest at its destination; source checked before the copy; copy.docx, cover.tif and logo.ai intact by digest at their recorded paths (CLM-0002-0002, CLM-0002-0003, CLM-0002-0004); brief.pdf not checked (recorded path not canonical); 6 ordinary assets checked by metadata only; 5 listings complete to depth 8 (1 memory listing, 4 size-filtered searches); 9 digests computed in this session before this receipt"
- pending: ["AST-0001-0001 brief.pdf (VER-0001-0001): out of scope, state unknown, not recovered (OPN-0002-0001)"]
- reason: "Entry ENT-0002-01-01 (layout.indd, VER-0001-0006) verified. Delivery 2 member brief.pdf stays pending because its recorded path is not canonical and was not read, so the target set SET-0001-0002 is not shown complete."

## RECORD REN-0002-01-01
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: "ENT-0002-01-01"
- asset_id: "AST-0001-0006"
- version_id: "VER-0001-0006"
- status: "verified"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd"
- source_sha256_before: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- destination_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- source_sha256_after: null
- note: "source re-hashed before the copy (OBS-0002-0018); destination digest equals VER-0001-0006 (OBS-0002-0020); source not re-hashed after because the destination matched"

## RECORD REN-0002-01-02
- type: "receipt-entry"
- receipt_id: "RCP-0002-01"
- entry_id: null
- asset_id: "AST-0001-0001"
- version_id: "VER-0001-0001"
- status: "out-of-scope"
- destination_path: null
- source_sha256_before: null
- destination_sha256: null
- source_sha256_after: null
- note: "recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical; listed as pending in PLN-0002-01 and not executed"
