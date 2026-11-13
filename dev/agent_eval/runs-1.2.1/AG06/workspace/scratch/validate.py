import json,re,sys
d=json.load(open('scratch/d4_bundles.json',encoding='utf-8'))
ids={}
recs={}
for f in d['result']['files']:
    lines=f['text'].split('\n')
    cur=None
    for ln in lines[1:]:
        if not ln: continue
        m=re.match(r'^## RECORD (\S+)$',ln)
        if m:
            cur=m.group(1); 
            if cur in recs: print('DUP',cur)
            recs[cur]={}; continue
        m=re.match(r'^- ([a-z0-9_]+): (.*)$',ln)
        if not m: print('BAD LINE',ln); continue
        v=json.loads(m.group(2))
        if cur: recs[cur][m.group(1)]=v
refs=set()
def walk(v):
    if isinstance(v,str) and re.match(r'^[A-Z]{2,3}-\d{4}',v): refs.add(v)
    elif isinstance(v,list): [walk(x) for x in v]
    elif isinstance(v,dict): [walk(x) for x in v.values()]; [walk(k) for k in v.keys()]
for r,fs in recs.items():
    for k,v in fs.items():
        if k in ('type',): continue
        walk(v)
missing=[x for x in refs if x not in recs]
print('records',len(recs),'missing refs',missing)
