import json,sys
def J(v): return json.dumps(v, ensure_ascii=False)
def bundle(bid, case, scope, recs):
    out=[f"# CERBERO BUNDLE {bid}", f"- schema: {J('cerbero-memory-2')}", f"- bundle_id: {J(bid)}", f"- case_id: {J(case)}", f"- scope_id: {J(scope)}", "- supersedes: null"]
    for rid, fields in recs:
        out.append(""); out.append(f"## RECORD {rid}")
        for k,v in fields:
            out.append(f"- {k}: {J(v)}")
    return "\n".join(out)+"\n"
