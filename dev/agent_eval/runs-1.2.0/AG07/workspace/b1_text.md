# CERBERO BUNDLE B-0003-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0003-01"
- case_id: "CAS-0003"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0003
- type: "case"
- scope_id: "SCP-0001"
- request: "learn"
- status: "open"
- opened_in: "session 0003"

## RECORD STM-0003-0001
- type: "statement"
- text: "Last session closed case CAS-0002 on project Aurora: the raw original DSC_0142.ARW was lost with no copy. Improve the next review. Synthetic test cases I authorize are in the memory folder."
- given_in: "session 0003, request"
- class: "user-declared"

## RECORD STM-0003-0002
- type: "statement"
- text: "Yes. I confirm the outcome of CAS-0002 as its receipt shows: three files verified, Delivery 2 complete, raw/DSC_0142.ARW lost with no copy in the named locations."
- given_in: "session 0003, reply to the test-data and outcome question"
- class: "user-declared"

## RECORD CAS-0002-0003
- type: "case"
- scope_id: "SCP-0001"
- request: "investigate-recover"
- status: "closed"
- opened_in: "session 0002"
- supersedes: "CAS-0002"

## RECORD OBS-0003-0001
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D3"
- state: "completed"
- result: "8 CERBERO- files in /data/studio/cerbero-memory, truncated false; newest index CERBERO-IDX-0002-01.md; no CERBERO-TH- file"
- coverage: "complete: 8 entries below the limit of 200, not truncated, no unreadable folder named"
- observed_at: "unknown"
- class: "observed"

## RECORD OBS-0003-0002
- type: "observation"
- check_card: null
- agent: "file-agent"
- delegation: "D7"
- state: "completed"
- result: "B-0001-01, B-0001-02, B-0002-01, B-0002-02, B-0002-03 equal to their IDX-0002-01 digests; CERBERO-TD-0000-01.md digest 27215cd7d4d914c58cc34d3b2800189c6301de54349a56718983451d4068bcb3, 1157 bytes, not listed in IDX-0002-01"
- coverage: "6 of 6 memory files requested hashed"
- observed_at: "unknown"
- class: "observed"

## RECORD CLM-0003-0001
- type: "claim"
- kind: "memory-trust"
- subject: "/data/studio/cerbero-memory/CERBERO-TD-0000-01.md"
- statement: "TD-0000-01 was needs-review (not listed in IDX-0002-01); accepted as the synthetic test data the user authorized, on the user words in STM-0003-0001 and STM-0003-0002; the user did not name the file explicitly"
- class: "user-declared"
- supports: ["STM-0003-0001", "STM-0003-0002", "OBS-0003-0002"]
- contradicts: []
- depends_on: ["STM-0003-0001", "/data/studio/cerbero-memory/CERBERO-TD-0000-01.md@27215cd7d4d914c58cc34d3b2800189c6301de54349a56718983451d4068bcb3"]
- status: "current"

## RECORD OPN-0003-0001
- type: "open-item"
- subject: "/data/studio/projects/aurora/exports/previews"
- reason: "no user statement declares this folder regenerable; asked in session 0003, the reply did not answer it"
- needed_to_resolve: "an explicit user declaration; until then the informational line of POL-0003-0001 changes nothing in SCP-0001"

## RECORD POL-0003-0001
- type: "policy"
- version: "v1"
- status: "candidate"
- condition: "A review (Investigate, Baseline or What-if) of scope SCP-0001, project /data/studio/projects/aurora. The informational line applies only to a folder that a current user-declared statement records as regenerable; at freeze time no such statement exists for SCP-0001."
- scope: "SCP-0001"
- effect: ["promote-critical raw", "add-recoverability-check project-volume", "informational exports/previews"]
- motivated_by: "CAS-0002-0003"
- drafted_from: ["TST-0000-0001", "TST-0000-0002"]
- rule_sha256: null
- approval: null