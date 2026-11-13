import json, sys, re
sys.path.insert(0, 'scratch')
from bundle import bundle, instruction
d = json.load(open('scratch/allrec.json', encoding='utf-8'))
entries = [
 ("/data/studio/cerbero-memory/CERBERO-B-0001-01.md", "B-0001-01", "8056343e9b83127a3cfa50579196f5d4787f2ac405c42be8b2a44bb186af1931", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0001-02.md", "B-0001-02", "bd00bb36e319d96ffd5a0b49353544a3d74c09d8d7f9fe7706b8c0e14d99d758", "current"),
 ("/data/studio/cerbero-memory/CERBERO-IDX-0001-01.md", "IDX-0001-01", "2f38a8093b55bc73033c33558d887da934b14073b413411e28469afb32ad35cc", "superseded"),
 ("/data/studio/cerbero-memory/CERBERO-B-0002-01.md", "B-0002-01", "ed52bcc309e5dd66dc4e52563af6bc0a6983df90cc1fe3f74446eaa0145bd985", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0002-02.md", "B-0002-02", "314b262e1dc95aa3fea53a37bb2a8f266278c7e9b4a39c0f8e968281bf04c754", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0002-03.md", "B-0002-03", "034a1711539896f3d043311fde69716a0a6c3cbfe4150e68414a38437cd379fc", "current"),
 ("/data/studio/cerbero-memory/CERBERO-IDX-0002-01.md", "IDX-0002-01", "f3c4d618480b3fb4bea47ba48c9eaab401014c47a61fac3b96678a959a9ca9b1", "superseded"),
 ("/data/studio/cerbero-memory/CERBERO-TD-0000-01.md", "TD-0000-01", "27215cd7c4d914c58cc34d3b2800189c6301de54349a56718983451d4068bcb3", "current"),
 ("/data/studio/cerbero-memory/CERBERO-TH-0000-01.md", "TH-0000-01", "da4f37783be68d2831d0e810b9289c15afb4fa2a75736094759360b9e71f11dd", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0003-01.md", "B-0003-01", "7e02691d1b9417bd8e4720039e9021440f82386262b072f0f7701a09465db80d", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0003-02.md", "B-0003-02", "f4338078177bbe4a68bb7fe4b88a18066c09131d1bc947784b91d4eb5751e2b1", "current"),
]
entries += [
 ("/data/studio/cerbero-memory/CERBERO-IDX-0003-01.md", "IDX-0003-01", "73d3b9556cf2131f576b25e86aff5732e914bbd757937851afa6c6119651458a", "superseded"),
 ("/data/studio/cerbero-memory/CERBERO-TH-0000-02.md", "TH-0000-02", "44d0bb6db0c781df0226a3139665667a32ef89b7a75a84d9a423b3b137b0c4a5", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0004-01.md", "B-0004-01", "cb236cf7ff4380c8fa2933ce885eed9c083123c479bb4bb688b2dcc650aa7032", "current"),
 ("/data/studio/cerbero-memory/CERBERO-B-0004-02.md", "B-0004-02", "61adef08531927de1fd4493199458824faeb66365646689ab274fa8745c38384", "current"),
]
records = []
for i, (f, b, s, st) in enumerate(entries, 1):
    records.append(("IDX-0004-01-%04d" % i, [("type","index-entry"),("file",f),("bundle_id",b),("sha256",s),("status",st)]))
text = bundle("IDX-0004-01", "CAS-0004", "SCP-0001", records)
open('scratch/IDX-0004-01.txt','w',encoding='utf-8',newline='').write(text)
open('scratch/d10_idx4.txt','w',encoding='utf-8',newline='').write(instruction("/data/studio/cerbero-memory", "CERBERO-IDX-0004-01", text))
print(len(text.encode('utf-8')), 'bytes', len(entries), 'entries')
for e in entries: print(e[1], e[3], e[2][:4]+'...'+e[2][-4:])
