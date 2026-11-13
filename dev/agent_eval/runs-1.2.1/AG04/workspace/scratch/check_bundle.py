import json, re, sys
p = sys.argv[1]
b = open(p, 'rb').read()
print('bytes', len(b), 'CR' if b'\r' in b else 'noCR', 'apostrophe' if b"'" in b else 'no-apostrophe', 'endsNL', b.endswith(b'\n'))
t = b.decode('utf-8')
lines = t.split('\n')
assert lines[0].startswith('# CERBERO BUNDLE '), lines[0]
ids = []
cur = None
fields = set()
for i, l in enumerate(lines[1:], 2):
    if not l:
        continue
    m = re.fullmatch(r'## RECORD (\S+)', l)
    if m:
        ids.append(m.group(1)); fields = set(); continue
    m = re.fullmatch(r'- ([a-z0-9_]+): (.*)', l)
    if not m:
        print('BAD LINE', i, l); continue
    if m.group(1) in fields:
        print('DUP FIELD', i, l)
    fields.add(m.group(1))
    try:
        json.loads(m.group(2))
    except Exception as e:
        print('BAD JSON', i, l, e)
print('records', len(ids), 'dups', [x for x in ids if ids.count(x) > 1])
