# CERBERO BUNDLE B-0004-01
- schema: "cerbero-memory-2"
- bundle_id: "B-0004-01"
- case_id: "CAS-0004"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD CAS-0004
- type: "case"
- scope_id: "SCP-0001"
- request: "learn"
- status: "open"
- opened_in: "this session"

## RECORD STM-0004-0001
- type: "statement"
- text: "The outcome of CAS-0002 is confirmed: 3 copies verified, Delivery 2 complete, raw/DSC_0142.ARW lost with no copy in the named locations."
- given_in: "this session"
- class: "user-declared"

## RECORD CAS-0002-0004
- type: "case"
- scope_id: "SCP-0001"
- request: "investigate-recover"
- status: "closed"
- opened_in: "this session"
- supersedes: "CAS-0002"

## RECORD POL-0004-0001
- type: "policy"
- status: "rejected"
- version: "v1"
- condition: "every review of an authorized project"
- scope: "project root"
- effect: ["promote-critical ."]
- motivated_by: "CAS-0002"
- drafted_from: ["TST-0000-0001", "TST-0000-0002"]
- rule_sha256: null
- approval: null

## RECORD EVL-0004-0001
- type: "evaluation"
- policy_id: "POL-0004-0001"
- rule_sha256: null
- verdict: "rejected"
- cases: ["TST-0000-0001 development origin fail", "TST-0000-0002 development counterexample fail"]

## RECORD POL-0004-0002
- type: "policy"
- version: "v2"
- condition: "every review of an authorized project"
- scope: "raw/ and exports/previews/ inside the project"
- effect: ["promote-critical raw", "informational exports/previews"]
- motivated_by: "CAS-0002"
- drafted_from: ["TST-0000-0001", "TST-0000-0002"]
- rule_sha256: null
- approval: null
- status: "candidate"
