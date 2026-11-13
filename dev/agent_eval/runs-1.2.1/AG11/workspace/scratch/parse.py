import json, re, glob, sys
recs = {}
files = sorted(glob.glob('CERBERO-*.md'))
for fn in files:
    lines = open(fn, encoding='utf-8').read().split('\n')
    title = lines[0]
    hdr = {}
    cur = None
    ok = True
    for ln in lines[1:]:
        if not ln: continue
        m = re.match(r'^## RECORD (\S+)$', ln)
        if m:
            cur = m.group(1)
            if cur in recs: print('DUP', cur, fn)
            recs[cur] = {'_file': fn}
            continue
        m = re.match(r'^- ([a-z0-9_]+): (.*)$', ln)
        if not m:
            print('BAD LINE', fn, ln); ok = False; continue
        k, v = m.group(1), json.loads(m.group(2))
        if cur is None:
            hdr[k] = v
        else:
            if k in recs[cur]: print('DUP FIELD', cur, k)
            recs[cur][k] = v
    print(fn, 'title ok' if title == '# CERBERO BUNDLE ' + hdr.get('bundle_id','') else 'TITLE MISMATCH', hdr.get('schema'), 'ok' if ok else 'BAD')
json.dump(recs, open('recs.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
# reference check
refpat = re.compile(r'^(SCP|AST|VER|CPY|LOC|DOM|SET|STM|CAS|CHK|OBS|CLM|HYP|OPN|FND|MAP|TST|PLN|ENT|APR|RCP|REN|POL|EVL)-\d{4}(-\d{2,4})*$')
def refs(v):
    if isinstance(v, str): return [v] if refpat.match(v) else []
    if isinstance(v, list): return [x for x in v for x in refs(x)]
    if isinstance(v, dict): return [x for k, y in v.items() for x in refs(k) + refs(y)]
    return []
for rid, r in recs.items():
    for k, v in r.items():
        if k in ('_file',): continue
        for x in refs(v):
            if x not in recs: print('MISSING REF', rid, k, x)
p1, p2, p3 = recs['POL-0004-0001'], recs['POL-0004-0002'], recs['POL-0004-0003']
for f in ('version', 'condition', 'scope', 'effect'):
    print(f, p1[f] == p2[f] == p3[f])
