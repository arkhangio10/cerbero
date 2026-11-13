# CERBERO BUNDLE B-0004-02
- schema: "cerbero-memory-2"
- bundle_id: "B-0004-02"
- case_id: "CAS-0004"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD EVL-0004-0002
- type: "evaluation"
- policy_id: "POL-0004-0002"
- rule_sha256: "c6e31f6703aecaa8f1aaba1624ee73a7194c073a9c8f594c048728fa9d158219"
- verdict: "evaluated"
- cases: ["TST-0000-0001 development origin pass", "TST-0000-0002 development counterexample pass", "TST-0000-0003 holdout similar pass", "TST-0000-0004 holdout insufficient pass", "TST-0000-0005 holdout similar pass"]

## RECORD POL-0004-0003
- type: "policy"
- status: "active"
- supersedes: "POL-0004-0002"
- version: "v2"
- condition: "every review of an authorized project"
- scope: "raw/ and exports/previews/ inside the project"
- effect: ["promote-critical raw", "informational exports/previews"]
- motivated_by: "CAS-0002"
- drafted_from: ["TST-0000-0001", "TST-0000-0002"]
- rule_sha256: "c6e31f6703aecaa8f1aaba1624ee73a7194c073a9c8f594c048728fa9d158219"
- approval: "Yes. I approve policy v2: raw/ is critical; exports/previews/ is informational."
