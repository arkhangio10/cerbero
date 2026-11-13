import json, re, sys
REQ = {'scope': ['real_root', 'name', 'authorized_by', 'newest_mtime'], 'asset': ['scope_id', 'name', 'recorded_path', 'importance', 'declared_by', 'current_version', 'recorded_size', 'recorded_mtime', 'observation'], 'version': ['asset_id', 'sha256', 'size_bytes', 'approved_by', 'observation'], 'approved-set': ['name', 'members', 'approved_by', 'status'], 'location': ['real_root', 'memberships', 'unknown_kinds', 'provenance', 'inventory'], 'domain': ['kind', 'label', 'parent', 'provenance'], 'copy': ['version_id', 'real_path', 'location_id', 'sha256', 'observation', 'access', 'status'], 'statement': ['text', 'given_in', 'class'], 'case': ['scope_id', 'request', 'status', 'opened_in'], 'check-card': ['doubt', 'decision', 'operation', 'outcomes', 'cost', 'budget_left'], 'observation': ['check_card', 'agent', 'delegation', 'state', 'result', 'coverage', 'observed_at', 'class'], 'claim': ['kind', 'subject', 'statement', 'class', 'supports', 'contradicts', 'depends_on', 'status'], 'hypothesis': ['subject', 'text', 'status', 'for', 'against', 'next_check'], 'open-item': ['subject', 'reason', 'needed_to_resolve'], 'finding': ['source', 'quote', 'kind', 'action_taken'], 'plan': ['case_id', 'revision', 'reference', 'target_set', 'recovery_folder', 'goal', 'preconditions', 'success_conditions', 'risks', 'pending', 'previous_receipt', 'supersedes_plan'], 'plan-entry': ['plan_id', 'asset_id', 'name', 'version_id', 'expected_sha256', 'size_bytes', 'source_path', 'destination_path'], 'approval': ['plan_id', 'plan_sha256', 'decision', 'statement'], 'receipt': ['plan_id', 'plan_sha256', 'overall', 'reference', 'set_complete', 'coverage', 'pending', 'reason'], 'receipt-entry': ['receipt_id', 'entry_id', 'asset_id', 'version_id', 'status', 'destination_path', 'source_sha256_before', 'destination_sha256', 'source_sha256_after', 'note'], 'index-entry': ['file', 'bundle_id', 'sha256', 'status']}
OPT = {'supersedes'}
REF_FIELDS = {'scope_id', 'authorized_by', 'declared_by', 'current_version', 'observation', 'asset_id', 'approved_by', 'provenance', 'parent', 'version_id', 'location_id', 'check_card', 'supports', 'contradicts', 'depends_on', 'for', 'against', 'case_id', 'target_set', 'previous_receipt', 'supersedes_plan', 'plan_id', 'receipt_id', 'entry_id', 'supersedes'}

trusted_ids = set()
for extra in sys.argv[2:]:
    trusted_ids |= set(re.findall(r'^## RECORD (\S+)$', open(extra, encoding='utf-8').read(), re.M))
text = open(sys.argv[1], encoding='utf-8').read()
lines = text.split('\n'); errs = []; recs = {}; hdr = {}; cur = None
for ln in lines[1:]:
    if not ln.strip():
        continue
    m = re.match(r'^## RECORD (\S+)$', ln)
    if m:
        if m.group(1) in recs: errs.append('dup rec ' + m.group(1))
        cur = m.group(1); recs[cur] = {}; continue
    m = re.match(r'^- ([a-z0-9_]+): (.*)$', ln)
    if not m: errs.append('bad line ' + ln[:80]); continue
    try: v = json.loads(m.group(2))
    except Exception: errs.append('bad json ' + ln[:80]); continue
    tgt = hdr if cur is None else recs[cur]
    if m.group(1) in tgt: errs.append('dup field ' + ln[:80])
    tgt[m.group(1)] = v
if lines[0] != '# CERBERO BUNDLE ' + str(hdr.get('bundle_id')): errs.append('title')
if set(hdr) != {'schema', 'bundle_id', 'case_id', 'scope_id', 'supersedes'} or hdr.get('schema') != 'cerbero-memory-2': errs.append('header')
ids = set(recs) | trusted_ids
for rid, r in recs.items():
    t = r.get('type')
    if t not in REQ: errs.append('unknown type ' + rid); continue
    for k in REQ[t]:
        if k not in r: errs.append(rid + ' missing ' + k)
    allowed = set(REQ[t]) | OPT | {'type'}
    if t == 'claim' and r.get('kind') == 'asset-state': allowed |= {'asset_state', 'located_at'}
    for k in r:
        if k not in allowed: errs.append(rid + ' extra field ' + k)
    for k in REF_FIELDS & set(r):
        v = r[k]; vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, str) and re.match(r'^[A-Z]{2,4}-\d{4}', x) and x not in ids: errs.append(rid + ' ref missing ' + k + '=' + x)
print(len(recs), 'records; errors:', errs)
