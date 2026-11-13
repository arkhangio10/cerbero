import json
M = "/data/studio/cerbero-memory/"
prev = [
 ("CERBERO-B-0001-01.md", "B-0001-01", "8056343e9b83127a3cfa50579196f5d4787f2ac405c42be8b2a44bb186af1931", "current"),
 ("CERBERO-B-0001-02.md", "B-0001-02", "bd00bb36e319d96ffd5a0b49353544a3d74c09d8d7f9fe7706b8c0e14d99d758", "current"),
 ("CERBERO-IDX-0001-01.md", "IDX-0001-01", "2f38a8093b55bc73033c33558d887da934b14073b413411e28469afb32ad35cc", "superseded"),
 ("CERBERO-B-0002-01.md", "B-0002-01", "ed52bcc309e5dd66dc4e52563af6bc0a6983df90cc1fe3f74446eaa0145bd985", "current"),
 ("CERBERO-B-0002-02.md", "B-0002-02", "314b262e1dc95aa3fea53a37bb2a8f266278c7e9b4a39c0f8e968281bf04c754", "current"),
 ("CERBERO-B-0002-03.md", "B-0002-03", "034a1711539896f3d043311fde69716a0a6c3cbfe4150e68414a38437cd379fc", "current"),
 ("CERBERO-IDX-0002-01.md", "IDX-0002-01", "f3c4d618480b3fb4bea47ba48c9eaab401014c47a61fac3b96678a959a9ca9b1", "superseded"),
 ("CERBERO-TD-0000-01.md", "TD-0000-01", "27215cd7c4d914c58cc34d3b2800189c6301de54349a56718983451d4068bcb3", "current"),
 ("CERBERO-TH-0000-01.md", "TH-0000-01", "da4f37783be68d2831d0e810b9289c15afb4fa2a75736094759360b9e71f11dd", "current"),
 ("CERBERO-B-0003-01.md", "B-0003-01", "7e02691d1b9417bd8e4720039e9021440f82386262b072f0f7701a09465db80d", "current"),
 ("CERBERO-B-0003-02.md", "B-0003-02", "f4338078177bbe4a68bb7fe4b88a18066c09131d1bc947784b91d4eb5751e2b1", "current"),
 ("CERBERO-IDX-0003-01.md", "IDX-0003-01", "73d3b9556cf2131f576b25e86aff5732e914bbd757937851afa6c6119651458a", "superseded"),
 ("CERBERO-TH-0000-02.md", "TH-0000-02", "44d0bb6db0c781df0226a3139665667a32ef89b7a75a84d9a423b3b137b0c4a5", "current"),
 ("CERBERO-B-0004-01.md", "B-0004-01", "cb236cf7ff4380c8fa2933ce885eed9c083123c479bb4bb688b2dcc650aa7032", "current"),
 ("CERBERO-B-0004-02.md", "B-0004-02", "61adef08531927de1fd4493199458824faeb66365646689ab274fa8745c38384", "current"),
 ("CERBERO-IDX-0004-01.md", "IDX-0004-01", "0a1b51c1110dc8e875a6ac118380e812985673c13bfe665e8e41665c04f692b6", "superseded"),
 ("CERBERO-B-0005-01.md", "B-0005-01", "58b7ad4a6a3f14362ff97ee8a8406ab61a16ced9efd61d13dd0759c163fc3ffc", "current"),
 ("CERBERO-IDX-0005-01.md", "IDX-0005-01", "8b2bfbf61efe1aaa7db1f43ba6bb2ddb715a6ad4942da5f0308dcf27427268f0", "superseded"),
 ("CERBERO-B-0006-01.md", "B-0006-01", "cd553b2e38e23ee34bc5b5e4ee1a60b5a77052acddd53c58c06220f4146a97b0", "current"),
 ("CERBERO-IDX-0006-01.md", "IDX-0006-01", "bdcff915468df909a9aed1566b90e4002eaffc729cb42f112535ffbeda159388", "superseded"),
 ("CERBERO-B-0007-01.md", "B-0007-01", "d8e8b9d1bd47347c731e43ed876d4095617eca2dad5a82bf31afe831a436ae9e", "current"),
]
lines = ["# CERBERO BUNDLE IDX-0007-01",
         '- schema: "cerbero-memory-2"',
         '- bundle_id: "IDX-0007-01"',
         '- case_id: "CAS-0007"',
         '- scope_id: "SCP-0001"',
         "- supersedes: null"]
for i, (f, bid, sha, st) in enumerate(prev, 1):
    lines += ["", "## RECORD IDX-0007-01-%04d" % i,
              '- type: "index-entry"',
              "- file: " + json.dumps(M + f),
              "- bundle_id: " + json.dumps(bid),
              "- sha256: " + json.dumps(sha),
              "- status: " + json.dumps(st)]
text = "\n".join(lines)
open("scratch/IDX-0007-01.md", "w", encoding="utf-8", newline="").write(text)
print(len(text.encode("utf-8")), "entries", len(prev))
