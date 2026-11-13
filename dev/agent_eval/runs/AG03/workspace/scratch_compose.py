import json, sys
Q = chr(39)
J = lambda v: json.dumps(v, ensure_ascii=False)


def bundle_text(bundle_id, case_id, scope_id, recs):
    out = ["# CERBERO BUNDLE " + bundle_id, "- schema: " + J("cerbero-memory-2"), "- bundle_id: " + J(bundle_id),
           "- case_id: " + J(case_id), "- scope_id: " + J(scope_id), "- supersedes: null", ""]
    for rid, f in recs:
        out.append("## RECORD " + rid)
        for k, v in f.items():
            out.append("- " + k.rstrip("_") + ": " + J(v))
        out.append("")
    return "\n".join(out)


def write_d10(sh_path, hint, text):
    assert Q not in text
    instr = ("Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint "
             + hint + ". Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: " + text)
    esc = instr.replace(Q, Q + '"' + Q + '"' + Q)
    open(sh_path, "w", encoding="utf-8", newline="\n").write("bash nas.sh delegate --target knowledge-agent --instruction " + Q + esc + Q + "\n")


if __name__ == "__main__":
    src = sys.argv[1]
    ns = {}
    exec(open(src, encoding="utf-8").read(), ns)
    text = bundle_text(ns["BUNDLE_ID"], ns["CASE_ID"], ns["SCOPE_ID"], ns["RECS"])
    open(ns["OUT_MD"], "w", encoding="utf-8", newline="\n").write(text)
    write_d10(ns["OUT_SH"], ns["HINT"], text)
    print(len(ns["RECS"]), "records", len(text.encode("utf-8")), "bytes")
