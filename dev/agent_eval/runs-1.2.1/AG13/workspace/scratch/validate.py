import json, re, sys, glob, os
REQ = {
 "scope":["real_root","name","authorized_by","newest_mtime"],
 "asset":["scope_id","name","recorded_path","importance","declared_by","current_version","recorded_size","recorded_mtime","observation"],
 "version":["asset_id","sha256","size_bytes","approved_by","observation"],
 "approved-set":["name","members","approved_by","status"],
 "location":["real_root","memberships","unknown_kinds","provenance","inventory"],
 "domain":["kind","label","parent","provenance"],
 "copy":["version_id","real_path","location_id","sha256","observation","access","status"],
 "statement":["text","given_in","class"],
 "case":["scope_id","request","status","opened_in"],
 "check-card":["doubt","decision","operation","outcomes","cost","budget_left"],
 "observation":["check_card","agent","delegation","state","result","coverage","observed_at","class"],
 "claim":["kind","subject","statement","class","supports","contradicts","depends_on","status"],
 "hypothesis":["subject","text","status","for","against","next_check"],
 "open-item":["subject","reason","needed_to_resolve"],
 "finding":["source","quote","kind","action_taken"],
 "map":["subject","scenario","verdict","members","evidence_level","unknowns"],
 "plan":["case_id","revision","reference","target_set","recovery_folder","goal","preconditions","success_conditions","risks","pending","previous_receipt","supersedes_plan"],
 "plan-entry":["plan_id","asset_id","name","version_id","expected_sha256","size_bytes","source_path","destination_path"],
 "approval":["plan_id","plan_sha256","decision","statement"],
 "receipt":["plan_id","plan_sha256","overall","reference","set_complete","coverage","pending","reason"],
 "receipt-entry":["receipt_id","entry_id","asset_id","version_id","status","destination_path","source_sha256_before","destination_sha256","source_sha256_after","note"],
 "test-case":["kind","split","facts","expected","source"],
 "policy":["version","status","condition","scope","effect","motivated_by","drafted_from","rule_sha256","approval"],
 "evaluation":["policy_id","rule_sha256","cases","verdict"],
 "index-entry":["file","bundle_id","sha256","status"],
}
REFFIELDS = {"authorized_by","scope_id","declared_by","current_version","observation","asset_id","approved_by","provenance","parent","version_id","location_id","check_card","subject_ref","plan_id","receipt_id","entry_id","target_set","previous_receipt","supersedes_plan","policy_id","motivated_by","supersedes","case_id"}
LISTREF = {"supports","contradicts","drafted_from"}
field_re = re.compile(r'^- ([a-z0-9_]+): (.*)$')
records = {}
problems = []
for path in sorted(glob.glob(sys.argv[1])):
    name = os.path.basename(path)
    lines = open(path, encoding='utf-8', newline='').read().split('\n')
    title = lines[0]
    m = re.match(r'^# CERBERO BUNDLE (\S+)$', title)
    if not m: problems.append((name,'bad title')); continue
    hdr = {}; cur=None; recs={}
    for ln in lines[1:]:
        if ln == '': continue
        h = re.match(r'^## RECORD (\S+)$', ln)
        if h:
            cur = h.group(1)
            if cur in recs: problems.append((name,'dup record '+cur))
            recs[cur] = {}
            continue
        f = field_re.match(ln)
        if not f: problems.append((name,'bad line '+ln[:60])); continue
        try: v = json.loads(f.group(2))
        except Exception as e: problems.append((name,'bad json '+ln[:60])); continue
        tgt = hdr if cur is None else recs[cur]
        if f.group(1) in tgt: problems.append((name,'dup field %s in %s'%(f.group(1),cur)))
        tgt[f.group(1)] = v
    for k in ["schema","bundle_id","case_id","scope_id","supersedes"]:
        if k not in hdr: problems.append((name,'missing header '+k))
    if hdr.get("schema")!="cerbero-memory-2": problems.append((name,'schema'))
    if hdr.get("bundle_id")!=m.group(1): problems.append((name,'bundle id mismatch'))
    for rid, r in recs.items():
        t = r.get("type")
        if t not in REQ: problems.append((name, 'unknown type %s %s'%(rid,t))); continue
        for k in REQ[t]:
            if k not in r: problems.append((name,'missing %s in %s'%(k,rid)))
        if rid in records: problems.append((name,'record id seen in another file '+rid))
        records[rid] = (name, r)
# reference check
ids = set(records)
for rid,(name,r) in records.items():
    for k,v in r.items():
        if k in REFFIELDS and isinstance(v,str) and re.match(r'^[A-Z]{2,3}-\d{4}',v) and v not in ids:
            problems.append((name,'%s.%s -> missing %s'%(rid,k,v)))
        if k in LISTREF and isinstance(v,list):
            for x in v:
                if re.match(r'^[A-Z]{2,3}-\d{4}',x) and x not in ids: problems.append((name,'%s.%s -> missing %s'%(rid,k,x)))
        if k=="members" and isinstance(v,dict) and r.get("type")=="approved-set":
            for a,b in v.items():
                for x in (a,b):
                    if x not in ids: problems.append((name,'%s members -> missing %s'%(rid,x)))
        if k=="memberships" and isinstance(v,dict):
            for x in v.values():
                if x not in ids: problems.append((name,'%s memberships -> missing %s'%(rid,x)))
print("records:", len(records))
print("problems:", len(problems))
for p in problems: print(p)
