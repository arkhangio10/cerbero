import json, re, glob, os
field_re = re.compile(r'^- ([a-z0-9_]+): (.*)$')
R = {}
for path in sorted(glob.glob('scratch/mem/CERBERO-B-*.md')):
    cur=None
    for ln in open(path,encoding='utf-8').read().split('\n')[1:]:
        h = re.match(r'^## RECORD (\S+)$', ln)
        if h: cur=h.group(1); R[cur]={'_file':os.path.basename(path)}; continue
        f = field_re.match(ln)
        if f and cur: R[cur][f.group(1)] = json.loads(f.group(2))
superseded = {r['supersedes'] for r in R.values() if r.get('supersedes')}
def inside(p, root):
    pc=p.split('/'); rc=root.split('/')
    if any(c in ('','.','..') for c in pc[1:]) or chr(92) in p: return False
    return pc[:len(rc)]==rc
# scenario: volume DOM-0001-0001
D='DOM-0001-0001'
def chain(dom):
    out=[]; seen=set()
    while dom and dom not in seen:
        seen.add(dom); out.append(dom); dom=R[dom]['parent']
    return out
Dchain = chain(D)  # D and ancestors
def loc_effect(loc):
    L=R[loc]; mem=L['memberships']
    # excluded if member of D directly or through child domain
    for k,d in mem.items():
        if D in chain(d): return 'excluded'
    # outside if member of a different domain of same kind as D or of an ancestor kind
    for anc in Dchain:
        kind=R[anc]['kind']
        if kind in mem and mem[kind]!=anc and anc not in chain(mem[kind]):
            return 'outside (%s %s != %s)'%(kind, mem[kind], anc)
    return 'uncertain'
for l in ['LOC-0001-0001','LOC-0001-0002','LOC-0001-0003','LOC-0001-0004']:
    print(l, R[l]['real_root'], loc_effect(l))
copies=[(k,v) for k,v in R.items() if v.get('type')=='copy' and k not in superseded]
def evaluate(ver):
    V=R[ver]; el=[]; un=[]; ex=[]
    for cid,c in copies:
        if c['version_id']!=ver: continue
        conds=[]
        if c['sha256'] is None: conds.append('uncertain:digest')
        elif c['sha256']!=V['sha256']: conds.append('excluded:digest')
        if c['access']=='denied': conds.append('excluded:access')
        elif c['access']!='readable': conds.append('uncertain:access')
        if not c.get('observation') or c['observation'] not in R: conds.append('uncertain:provenance')
        if c['status']=='superseded': conds.append('excluded:status')
        elif c['status']=='needs-review': conds.append('uncertain:status')
        L=R.get(c['location_id'])
        if L is None: conds.append('uncertain:location')
        elif not inside(c['real_path'], L['real_root']): conds.append('excluded:location')
        eff=loc_effect(c['location_id']) if L else 'uncertain'
        if eff=='excluded': conds.append('excluded:scenario')
        elif eff=='uncertain': conds.append('uncertain:scenario')
        if any(x.startswith('excluded') for x in conds): ex.append((cid,conds))
        elif conds: un.append((cid,conds))
        else: el.append((cid,c['real_path']))
    return el,un,ex
for sid in ['SET-0001-0002','SET-0001-0001']:
    S=R[sid]; print('\n',sid,S['name'],S['status'])
    for a,v in S['members'].items():
        el,un,ex=evaluate(v)
        print(' ',R[a]['name'],v,R[v]['sha256'][:4]+'...'+R[v]['sha256'][-4:],R[v]['size_bytes'],'eligible',len(el),[e[0]+' '+e[1] for e in el],'uncertain',len(un),un,'excluded',[e[0] for e in ex])
print('\nother recorded versions')
setvers={v for s in ['SET-0001-0001','SET-0001-0002'] for v in R[s]['members'].values()}
for k,v in R.items():
    if v.get('type')=='version' and k not in setvers:
        el,un,ex=evaluate(k)
        print(' ',k,R[v['asset_id']]['name'],R[v['asset_id']]['importance'],v['sha256'][:4]+'...'+v['sha256'][-4:],v['size_bytes'],'eligible',len(el),'uncertain',len(un),'excluded',[e[0] for e in ex])
# receipt evidence
print('\nreceipt check')
for k,v in R.items():
    if v.get('type')=='receipt-entry' and v['status']=='verified':
        rc=R[v['receipt_id']]; en=R[v['entry_id']]; ap=[a for a in R.values() if a.get('type')=='approval' and a['plan_id']==rc['plan_id']]
        ver=R[v['version_id']]
        src=[cid for cid,c in copies if c['real_path']==en['source_path'] and c['version_id']==en['version_id']]
        ok = ap and ap[0]['decision']=='granted' and ap[0]['plan_sha256']==rc['plan_sha256'] and ver['sha256']==en['expected_sha256']==v['source_sha256_before']==v['destination_sha256']
        print(' ',k,en['name'],'copy',src,'ok',ok, rc['plan_sha256'][:4])
