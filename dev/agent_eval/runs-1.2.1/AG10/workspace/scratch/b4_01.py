import json, sys
sys.path.insert(0, 'scratch')
from bundle import bundle, instruction
req = open('REQUEST.md', encoding='utf-8').read().strip()
cond = ("Any Baseline, What-if or Investigate review of a project folder that the user names in that review and that D2 resolves in that session. "
        "The folders below are relative to that real project root, and this policy never authorizes, adds or searches any folder, location or project by itself. "
        "The line promote-critical raw applies to the folder raw directly inside that project root whenever it exists: its files are digested in every review within the session budget and included in the recoverability map, "
        "and a raw file with no eligible copy outside a failed location or domain is reported as at risk in that scenario. "
        "A copy at a location whose domain membership is unknown is reported as uncertain, and a raw file left unhashed or seen only in a possibly incomplete listing is reported by name as not reviewed; neither is ever reported as safe or as lost. "
        "The line promote-critical raw does not apply while a current user-declared statement says that the raw folder of that same project holds regenerable files, except to a file that is a user-declared critical asset or an approved-set member, which keeps its full review. "
        "The line informational exports/previews applies only while a current user-declared statement says that exports/previews of that same project holds regenerable files, and never to a file that is a user-declared critical asset or an approved-set member; "
        "until such a statement exists, exports/previews of that project is reviewed as without this policy. An informational change is still reported with its path and digest.")
scope = ("The folders raw and exports/previews directly inside the real root of each project folder that the user names in a review and D2 resolves in that session; "
         "no other folder, location or project, and nothing outside that real root.")
records = [
 ("CAS-0004", [("type","case"),("scope_id","SCP-0001"),
   ("request","learn: draft version 2 of the lesson from closed case CAS-0002 (CAS-0002-0003), revising rejected policy POL-0003-0002 version 1, from the development cases only"),
   ("status","open"),("opened_in","this session")]),
 ("STM-0004-0001", [("type","statement"),("text",req),("given_in","this session, the request"),("class","user-declared")]),
 ("POL-0004-0001", [("type","policy"),("version","2"),("status","candidate"),("condition",cond),("scope",scope),
   ("effect",["promote-critical raw","informational exports/previews"]),
   ("motivated_by","CAS-0002-0003"),("drafted_from",["TST-0000-0001","TST-0000-0002"]),
   ("rule_sha256",None),("approval",None)]),
 ("OPN-0004-0001", [("type","open-item"),("subject","POL-0004-0001"),
   ("reason","the development cases cover only the kinds origin (TST-0000-0001) and counterexample (TST-0000-0002); kinds similar and insufficient and at least one holdout case are missing. TST-0000-0003 to TST-0000-0005 in CERBERO-TH-0000-01.md were read before this freeze, in the session of CAS-0003, and the recorded reason of the failure of TST-0000-0003 (OPN-0003-0003) informed the scope of version 2, so they cannot be holdout cases for this candidate and are not used to draft it"),
   ("needed_to_resolve","new holdout test cases in a new TH- bundle that the user adds after this candidate is frozen, read only after the freeze"),
   ("supersedes","OPN-0003-0003")]),
]
text = bundle("B-0004-01", "CAS-0004", "SCP-0001", records)
open('scratch/B-0004-01.txt','w',encoding='utf-8',newline='').write(text)
ins = instruction("/data/studio/cerbero-memory", "CERBERO-B-0004-01", text)
open('scratch/d10_b4_01.txt','w',encoding='utf-8',newline='').write(ins)
print(len(text.encode('utf-8')), 'bytes of record text')
print(text)
