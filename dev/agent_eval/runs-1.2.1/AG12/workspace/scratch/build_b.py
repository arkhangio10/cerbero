import json
d = json.load(open('scratch/d4_bundles.json', encoding='utf-8'))
txt = {f['path'].rsplit('/', 1)[1]: f['text'] for f in d['result']['files']}

def records(text):
    recs, cur = {}, None
    for line in text.split('\n'):
        if line.startswith('## RECORD '):
            cur = line[10:]; recs[cur] = []
        elif cur and line.startswith('- '):
            recs[cur].append(line)
    return recs

pol = records(txt['CERBERO-B-0004-02.md'])['POL-0004-0003']
src = {l[2:].split(': ', 1)[0]: l[2:].split(': ', 1)[1] for l in pol}

def f(k, v): return f"- {k}: {json.dumps(v, ensure_ascii=False)}"

user_words = "Retire the active policy you learned from case CAS-0002. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora."

lines = [
"# CERBERO BUNDLE B-0006-01",
f("schema", "cerbero-memory-2"), f("bundle_id", "B-0006-01"), f("case_id", "CAS-0006"), f("scope_id", "SCP-0001"), f("supersedes", None),
"",
"## RECORD CAS-0006",
f("type", "case"), f("scope_id", "SCP-0001"),
f("request", "learn: retire the active policy learned from case CAS-0002 (POL-0004-0003 version 2, motivated by CAS-0002-0003)"),
f("status", "open"), f("opened_in", "this session"),
"",
"## RECORD STM-0006-0001",
f("type", "statement"), f("text", user_words), f("given_in", "this session, the request"), f("class", "user-declared"),
"",
"## RECORD OBS-0006-0001",
f("type", "observation"), f("check_card", None), f("agent", "file-agent"), f("delegation", "D1, D2"), f("state", "completed"),
f("result", "user folder /data/studio; /data/studio/projects/aurora and /data/studio/cerbero-memory exist, are readable and have real paths equal to the names given"),
f("coverage", "2 of 2 folders this request needs resolved; the three copy locations were not resolved because retiring a policy does not need them"),
f("observed_at", "unknown"), f("class", "observed"),
"",
"## RECORD OBS-0006-0002",
f("type", "observation"), f("check_card", None), f("agent", "file-agent"), f("delegation", "D3, D4, D7"), f("state", "completed"),
f("result", "D3 listed 18 CERBERO- files, not truncated; newest index IDX-0005-01 read in full (4110 bytes, digest 8b2bfbf61efe1aaa7db1f43ba6bb2ddb715a6ad4942da5f0308dcf27427268f0); B-0002-02, B-0002-03, B-0003-01, B-0003-02, B-0004-01, B-0004-02, B-0005-01 and TD-0000-01 read in full with byte counts equal to the listing, and their 8 digests equal the index digests; POL-0004-0003 (version 2, status active, in B-0004-02) is the newest record of its chain and the only active policy motivated by CAS-0002-0003; POL-0003-0002 (version 1) is rejected"),
f("coverage", "9 of 18 memory files read and hashed; B-0001-01, B-0001-02, B-0002-01, TH-0000-01, TH-0000-02 and the superseded snapshots IDX-0001-01 to IDX-0004-01 not read or hashed"),
f("observed_at", "unknown"), f("class", "observed"),
"",
"## RECORD POL-0006-0001",
f("type", "policy"),
f("version", json.loads(src["version"])), f("status", "retired"),
]
for k in ["condition", "scope", "effect", "motivated_by", "drafted_from", "rule_sha256"]:
    lines.append(f"- {k}: {src[k]}")
lines += [f("approval", "Retire the active policy you learned from case CAS-0002."), f("supersedes", "POL-0004-0003")]
text = "\n".join(lines) + "\n"
assert "'" not in text
open('scratch/B-0006-01.md', 'w', encoding='utf-8', newline='\n').write(text)
open('scratch/d10_b.txt', 'w', encoding='utf-8', newline='\n').write(
 "Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-B-0006-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: " + text)
print(len(text.encode('utf-8')))
