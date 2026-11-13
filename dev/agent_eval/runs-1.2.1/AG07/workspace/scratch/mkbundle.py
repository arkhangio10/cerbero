import json, sys

def bundle(bundle_id, case_id, scope_id, records):
    lines = [f"# CERBERO BUNDLE {bundle_id}",
             f"- schema: {json.dumps('cerbero-memory-2')}",
             f"- bundle_id: {json.dumps(bundle_id)}",
             f"- case_id: {json.dumps(case_id)}",
             f"- scope_id: {json.dumps(scope_id)}",
             f"- supersedes: null"]
    for rid, fields in records:
        lines.append("")
        lines.append(f"## RECORD {rid}")
        for k, v in fields:
            lines.append(f"- {k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"

D10 = ("Save the Markdown text below as a new text file in the folder {memory_root}, using the file name hint "
       "{record_file_hint}. Never replace or append to an existing file; if that name is taken, stop and report it. "
       "Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. "
       "Text: {record_text}")

def write(name, hint, text):
    assert "'" not in text
    instr = D10.replace("{memory_root}", "/data/studio/cerbero-memory").replace("{record_file_hint}", hint).replace("{record_text}", text)
    with open(name + ".txt", "w", encoding="utf-8", newline="\n") as f:
        f.write(instr)
    with open(name + ".bundle.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(name, "bytes of record text:", len(text.encode("utf-8")))
