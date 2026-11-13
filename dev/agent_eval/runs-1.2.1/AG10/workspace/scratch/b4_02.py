import json, sys, re
sys.path.insert(0, 'scratch')
from bundle import bundle, instruction
# reuse the frozen candidate fields exactly as saved
cand = {}
cur = None
for l in open('scratch/B-0004-01.txt', encoding='utf-8').read().split('\n'):
    m = re.match(r'^## RECORD (\S+)$', l)
    if m: cur = m.group(1); continue
    m = re.match(r'^- ([a-z0-9_]+): (.*)$', l)
    if m and cur == 'POL-0004-0001': cand[m.group(1)] = json.loads(m.group(2))
RULE = "cb236cf7ff4380c8fa2933ce885eed9c083123c479bb4bb688b2dcc650aa7032"
TH2 = "44d0bb6db0c781df0226a3139665667a32ef89b7a75a84d9a423b3b137b0c4a5"
def pol(status, approval, supersedes):
    return [("type","policy"),("version",cand["version"]),("status",status),("condition",cand["condition"]),("scope",cand["scope"]),
            ("effect",cand["effect"]),("motivated_by",cand["motivated_by"]),("drafted_from",cand["drafted_from"]),
            ("rule_sha256",RULE),("approval",approval),("supersedes",supersedes)]
records = [
 ("OBS-0004-0001", [("type","observation"),("check_card",None),("agent","file-agent"),("delegation","D7"),("state","completed"),
   ("result","/data/studio/cerbero-memory/CERBERO-B-0004-01.md digest " + RULE + ", 3791 bytes, after a D10 save reported verified with 3791 bytes"),
   ("coverage","1 of 1 files hashed"),("observed_at","unknown"),("class","observed")]),
 ("OBS-0004-0002", [("type","observation"),("check_card",None),("agent","file-agent"),("delegation","D3, D7, D4"),("state","completed"),
   ("result","after the freeze, D3 listed 14 CERBERO- files, not truncated, including the new /data/studio/cerbero-memory/CERBERO-TH-0000-02.md (964 bytes, modified 10000), absent from the D3 listing before the freeze; D7 digest " + TH2 + "; D4 returned 964 bytes with test cases TST-0000-0006 (similar, holdout) and TST-0000-0007 (insufficient, holdout)"),
   ("coverage","1 new holdout file hashed and read completely; CERBERO-TH-0000-01.md not read in this session"),("observed_at","unknown"),("class","observed")]),
 ("STM-0004-0002", [("type","statement"),("text","The test-case files in the memory folder, including any new holdout file, are synthetic data I placed and authorize. Continue."),
   ("given_in","this session, answer to the Cerbero question asking to add new holdout cases after the freeze of POL-0004-0001; covers CERBERO-TH-0000-02.md (sha256 " + TH2 + "), hashed after this answer"),
   ("class","user-declared")]),
 ("EVL-0004-0001", [("type","evaluation"),("policy_id","POL-0004-0001"),("rule_sha256",RULE),
   ("cases",["TST-0000-0001 development origin pass","TST-0000-0002 development counterexample pass","TST-0000-0006 holdout similar pass","TST-0000-0007 holdout insufficient pass"]),
   ("verdict","evaluated")]),
 ("POL-0004-0002", pol("evaluated", None, "POL-0004-0001")),
 ("STM-0004-0003", [("type","statement"),("text","Yes. I approve POL-0004-0001."),
   ("given_in","this session, answer to the Cerbero question: Do you approve policy POL-0004-0001 version 2? asked after showing evaluation EVL-0004-0001 with rule digest " + RULE),
   ("class","user-declared")]),
 ("POL-0004-0003", pol("active", "Yes. I approve POL-0004-0001.", "POL-0004-0002")),
 ("OPN-0004-0002", [("type","open-item"),("subject","POL-0004-0003"),
   ("reason","all four kinds are now covered: origin and counterexample in development, similar and insufficient in holdout (CERBERO-TH-0000-02.md, unseen before the freeze). Limits: the holdout cases come only from project Borealis; there is no holdout counterexample; the clause that skips promote-critical raw while the user declares a raw folder regenerable is exercised by no recorded case; TST-0000-0003 to TST-0000-0005 were not replayed against version 2 and are not counted"),
   ("needed_to_resolve","a holdout counterexample and a case that exercises the regenerable raw clause, if the user wants them; any change to the rule is a new version with a new evaluation"),
   ("supersedes","OPN-0004-0001")]),
]
text = bundle("B-0004-02", "CAS-0004", "SCP-0001", records)
open('scratch/B-0004-02.txt','w',encoding='utf-8',newline='').write(text)
open('scratch/d10_b4_02.txt','w',encoding='utf-8',newline='').write(instruction("/data/studio/cerbero-memory", "CERBERO-B-0004-02", text))
print(len(text.encode('utf-8')), 'bytes')
