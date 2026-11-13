import json, re, sys, glob
TYPES = {"scope","asset","version","approved-set","location","domain","copy","statement","case","check-card","observation","claim","hypothesis","open-item","finding","map","plan","plan-entry","approval","receipt","receipt-entry","test-case","policy","evaluation","index-entry"}
allrec = {}
for fn in sys.argv[1:]:
    t = open(fn, encoding='utf-8', newline='').read()
    lines = t.split('\n')
    errs = []
    if not lines[0].startswith('# CERBERO BUNDLE '):
        errs.append('title')
    hdr = {}
    recs = {}
    cur = None
    for i, l in enumerate(lines[1:], 2):
        if l == '':
            continue
        m = re.match(r'^## RECORD (\S+)$', l)
        if m:
            cur = m.group(1)
            if cur in recs: errs.append('dup record '+cur)
            recs[cur] = {}
            continue
        m = re.match(r'^- ([a-z0-9_]+): (.*)$', l)
        if not m:
            errs.append('bad line %d: %r' % (i, l[:80])); continue
        k, v = m.group(1), m.group(2)
        try:
            v = json.loads(v)
        except Exception:
            errs.append('bad json line %d' % i); continue
        tgt = hdr if cur is None else recs[cur]
        if k in tgt: errs.append('dup field %s line %d' % (k, i))
        tgt[k] = v
    if lines[0][len('# CERBERO BUNDLE '):] != hdr.get('bundle_id'):
        errs.append('title/bundle mismatch')
    for k in ('schema','bundle_id','case_id','scope_id','supersedes'):
        if k not in hdr: errs.append('missing header '+k)
    for rid, r in recs.items():
        if r.get('type') not in TYPES: errs.append('unknown type %s %s' % (rid, r.get('type')))
        if rid in allrec: errs.append('record in two files '+rid)
        allrec[rid] = (fn, r)
    print(fn, 'records', len(recs), 'errors', errs)
json.dump({k:v[1] for k,v in allrec.items()}, open('scratch/allrec.json','w',encoding='utf-8'), indent=1)
