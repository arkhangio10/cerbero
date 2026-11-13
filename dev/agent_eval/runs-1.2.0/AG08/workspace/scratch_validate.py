import json, re, sys
p = sys.argv[1]
raw = open(p, 'rb').read()
print('bytes', len(raw))
t = raw.decode('utf-8')
lines = t.split('\n')
ids = set(); bad = 0
for i, l in enumerate(lines):
    if not l or l.startswith('# CERBERO BUNDLE ') or l.startswith('## RECORD '):
        if l.startswith('## RECORD '):
            rid = l[10:]
            if rid in ids: print('dup', rid)
            ids.add(rid)
        continue
    m = re.match(r'^- ([a-z0-9_]+): (.*)$', l)
    if not m: print('badline', i, l); bad += 1; continue
    try: json.loads(m.group(2))
    except Exception as e: print('badjson', i, l); bad += 1
print('records', len(ids), 'bad', bad, "single quotes", t.count("'"))
