import json, sys

SQ = chr(39)
DQ = chr(34)
SHELL_SQ = SQ + DQ + SQ + DQ + SQ


def J(v):
    return json.dumps(v, ensure_ascii=False)


def render(bundle_id, case_id, scope_id, recs):
    lines = ["# CERBERO BUNDLE " + bundle_id, "- schema: " + J("cerbero-memory-2"), "- bundle_id: " + J(bundle_id),
             "- case_id: " + J(case_id), "- scope_id: " + J(scope_id), "- supersedes: null"]
    seen = set()
    for rid, fields in recs:
        assert rid not in seen, rid
        seen.add(rid)
        lines += ["", "## RECORD " + rid]
        keys = set()
        for k, v in fields:
            assert k not in keys, (rid, k)
            keys.add(k)
            lines.append("- %s: %s" % (k, J(v)))
    return "\n".join(lines) + "\n"


def write_save(bundle_id, text, sh_name):
    instr = ("Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-"
             + bundle_id + ". Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: " + text)
    esc = instr.replace(SQ, SHELL_SQ)
    with open(sh_name, "w", encoding="utf-8", newline="\n") as f:
        f.write("bash nas.sh delegate --target knowledge-agent --instruction " + SQ + esc + SQ + "\n")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    spec = load(sys.argv[1])
    recs = [(r["id"], [("type", r["type"])] + [(k, v) for k, v in r["fields"]]) for r in spec["records"]]
    text = render(spec["bundle_id"], spec["case_id"], spec["scope_id"], recs)
    with open("bundle_" + spec["bundle_id"] + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    write_save(spec["bundle_id"], text, "d10_" + spec["bundle_id"] + ".sh")
    print(len(text.encode("utf-8")), "bytes;", len(recs), "records; single quotes:", text.count(SQ))
