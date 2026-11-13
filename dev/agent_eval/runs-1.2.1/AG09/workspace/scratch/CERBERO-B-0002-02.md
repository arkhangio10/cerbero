# CERBERO BUNDLE B-0002-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0002-02"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD PLN-0002-01
- type: "plan"
- case_id: "CAS-0002"
- revision: 1
- reference: "approved-version"
- target_set: "SET-0001-0002"
- recovery_folder: "/data/studio/recovered/cerbero-recovery-CAS-0002"
- goal: "recover the changed members of SET-0001-0002 into recovered/cerbero-recovery-CAS-0002"
- preconditions: "user approved this plan ID and digest; source digest equals expected immediately before copy; destination absent; every path inside its authorized folder"
- success_conditions: "destination exists at the planned real path and its digest equals the expected digest; the target is complete only when every target member is in place or verified"
- risks: "no atomic copy; sources may change; NAS approval may be declined"
- pending: []
- previous_receipt: null
- supersedes_plan: null
- target_kind: "approved-set"
- target_members: ["AST-0001-0001", "AST-0001-0002", "AST-0001-0003", "AST-0001-0006", "AST-0001-0007"]
- outside_target: ["AST-0001-0010"]

## RECORD ENT-0002-01-01
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0002"
- name: "copy.docx"
- version_id: "VER-0001-0002"
- expected_sha256: "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495"
- size_bytes: 968
- source_path: "/data/studio/backups/aurora-2026-10-01/copy.docx"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/copy.docx"

## RECORD ENT-0002-01-02
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0003"
- name: "cover.tif"
- version_id: "VER-0001-0003"
- expected_sha256: "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911"
- size_bytes: 9396
- source_path: "/data/studio/backups/aurora-2026-10-01/cover.tif"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/cover.tif"

## RECORD ENT-0002-01-03
- type: "plan-entry"
- plan_id: "PLN-0002-01"
- asset_id: "AST-0001-0006"
- name: "layout.indd"
- version_id: "VER-0001-0006"
- expected_sha256: "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
- size_bytes: 16384
- source_path: "/data/studio/backups/aurora-2026-10-01/layout.indd"
- destination_path: "/data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd"
