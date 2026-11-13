import json, subprocess
idx_text = json.loads(open('scratch/idx5.json', encoding='utf-8').read())['result']['files'][0]['text']
entries, cur = [], None
for line in idx_text.split('\n'):
    if line.startswith('## RECORD '):
        cur = {}; entries.append(cur)
    elif cur is not None and line.startswith('- '):
        k, v = line[2:].split(': ', 1); cur[k] = json.loads(v)
entries = [e for e in entries]
entries.append({"type": "index-entry", "file": "/data/studio/cerbero-memory/CERBERO-IDX-0005-01.md", "bundle_id": "IDX-0005-01", "sha256": "8b2bfbf61efe1aaa7db1f43ba6bb2ddb715a6ad4942da5f0308dcf27427268f0", "status": "superseded"})
entries.append({"type": "index-entry", "file": "/data/studio/cerbero-memory/CERBERO-B-0006-01.md", "bundle_id": "B-0006-01", "sha256": "cd553b2e38e23ee34bc5b5e4ee1a60b5a77052acddd53c58c06220f4146a97b0", "status": "current"})
def f(k, v): return f"- {k}: {json.dumps(v, ensure_ascii=False)}"
lines = ["# CERBERO BUNDLE IDX-0006-01", f("schema", "cerbero-memory-2"), f("bundle_id", "IDX-0006-01"), f("case_id", "CAS-0006"), f("scope_id", "SCP-0001"), f("supersedes", None)]
for i, e in enumerate(entries, 1):
    lines += ["", f"## RECORD IDX-0006-01-{i:04d}"] + [f(k, e[k]) for k in ["type", "file", "bundle_id", "sha256", "status"]]
text = "\n".join(lines) + "\n"
assert "'" not in text
open('scratch/IDX-0006-01.md', 'w', encoding='utf-8', newline='\n').write(text)
open('scratch/d10_idx.txt', 'w', encoding='utf-8', newline='\n').write(
 "Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-IDX-0006-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: " + text)
print(len(entries), len(text.encode('utf-8')))
