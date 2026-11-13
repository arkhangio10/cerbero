import json, sys
def bundle(bid, case_id, scope_id, records, supersedes=None):
    out = ["# CERBERO BUNDLE " + bid]
    for k, v in (("schema", "cerbero-memory-2"), ("bundle_id", bid), ("case_id", case_id), ("scope_id", scope_id), ("supersedes", supersedes)):
        out.append("- %s: %s" % (k, json.dumps(v, ensure_ascii=False)))
    for rid, fields in records:
        out.append("")
        out.append("## RECORD " + rid)
        for k, v in fields:
            out.append("- %s: %s" % (k, json.dumps(v, ensure_ascii=False)))
    return "\n".join(out) + "\n"

def instruction(memory_root, hint, text):
    assert "'" not in text
    return ("Save the Markdown text below as a new text file in the folder " + memory_root +
            ", using the file name hint " + hint +
            ". Never replace or append to an existing file; if that name is taken, stop and report it. "
            "Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: " + text)
