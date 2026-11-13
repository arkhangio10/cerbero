from mkbundle import bundle, write
RULE = "7e02691d1b9417bd8e4720039e9021440f82386262b072f0f7701a09465db80d"
REPLY = "The test-case files in the memory folder are synthetic data I placed and authorize. Continue."
COND = ("Any Baseline, What-if or Investigate review of scope SCP-0001 (real root /data/studio/projects/aurora). The line promote-critical raw applies always. "
        "The line informational exports/previews applies only while a current user-declared statement says that exports/previews holds regenerable files, "
        "and never to a file that is a user-declared critical asset or an approved-set member; until such a statement exists, exports/previews is reviewed as without this policy.")
SCOPE = "SCP-0001, folders raw and exports/previews relative to the project root /data/studio/projects/aurora; no other folder or location"
records = [
 ("STM-0003-0003", [("type","statement"),("text",REPLY),("given_in","this session, answer to the Cerbero question on the evaluation of POL-0003-0001, on CERBERO-TH-0000-01.md (sha256 da4f37783be68d2831d0e810b9289c15afb4fa2a75736094759360b9e71f11dd) and on drafting version 2"),("class","user-declared")]),
 ("EVL-0003-0001", [("type","evaluation"),("policy_id","POL-0003-0001"),("rule_sha256",RULE),
   ("cases",["TST-0000-0001 development origin pass","TST-0000-0002 development counterexample pass","TST-0000-0003 holdout similar fail","TST-0000-0004 holdout insufficient pass","TST-0000-0005 holdout similar pass"]),
   ("verdict","rejected")]),
 ("POL-0003-0002", [("type","policy"),("version","1"),("status","rejected"),("condition",COND),("scope",SCOPE),
   ("effect",["promote-critical raw","informational exports/previews"]),("motivated_by","CAS-0002-0003"),
   ("drafted_from",["TST-0000-0001","TST-0000-0002"]),("rule_sha256",RULE),("approval",None),("supersedes","POL-0003-0001")]),
 ("OPN-0003-0003", [("type","open-item"),("subject","POL-0003-0001"),
   ("reason","all four test-case kinds now exist with holdout cases in CERBERO-TH-0000-01.md, read only after the freeze; version 1 was rejected because holdout similar case TST-0000-0003 (project Borealis) fails: the rule scope is limited to SCP-0001; the user answer did not choose between drafting version 2 and stopping"),
   ("needed_to_resolve","an explicit user request for version 2 (same effect lines, scope: the raw folder of any project the user authorizes in a review) and new holdout cases added after its freeze; TST-0000-0003 to TST-0000-0005 were seen and cannot be holdout cases for it"),
   ("supersedes","OPN-0003-0001")]),
]
text = bundle("B-0003-02","CAS-0003","SCP-0001",records)
write("d10_b0003_02","CERBERO-B-0003-02",text)
