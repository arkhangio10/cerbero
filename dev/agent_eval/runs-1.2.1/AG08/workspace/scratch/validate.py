import json,re,sys
d=json.load(open('scratch/d4_bundles.json',encoding='utf-8'))
ids={}
allrefs=[]
for f in d['result']['files']:
    t=f['text']; lines=t.split('\n')
    errs=[]
    if not lines[0].startswith('# CERBERO BUNDLE '): errs.append('title')
    hdr={}; cur=None; recs={}
    for ln in lines[1:]:
        if ln=='' : continue
        m=re.match(r'^## RECORD (\S+)$',ln)
        if m:
            cur=m.group(1)
            if cur in recs: errs.append('dup '+cur)
            recs[cur]={}; continue
        m=re.match(r'^- ([a-z0-9_]+): (.*)$',ln)
        if not m: errs.append('bad line '+ln); continue
        k,v=m.group(1),m.group(2)
        try: v=json.loads(v)
        except Exception as e: errs.append('json '+ln)
        tgt=hdr if cur is None else recs[cur]
        if k in tgt: errs.append('dupfield %s %s'%(cur,k))
        tgt[k]=v
    for r in recs:
        if r in ids: errs.append('id in two files '+r)
        ids[r]=f['path']
    print(f['path'], 'hdr', hdr, 'records', len(recs), 'errs', errs, 'endsNL', t.endswith('\n'), 'bytes', len(t.encode('utf-8')))
    for r,v in recs.items():
        for k,val in v.items():
            if k in ('type',): continue
            vals = val if isinstance(val,list) else (list(val.values()) if isinstance(val,dict) else [val])
            for x in vals:
                if isinstance(x,str) and re.match(r'^(SCP|AST|VER|CPY|LOC|DOM|SET|STM|CAS|CHK|OBS|CLM|HYP|OPN|FND|MAP|TST|PLN|ENT|APR|RCP|REN|POL|EVL)-[0-9-]+$',x):
                    allrefs.append((r,k,x))
missing=[(r,k,x) for r,k,x in allrefs if x not in ids]
print('missing refs', missing)
