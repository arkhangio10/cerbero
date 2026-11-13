import json
recs = json.load(open('recs.json', encoding='utf-8'))
req = {
'scope':'real_root name authorized_by newest_mtime','asset':'scope_id name recorded_path importance declared_by current_version recorded_size recorded_mtime observation',
'version':'asset_id sha256 size_bytes approved_by observation','approved-set':'name members approved_by status','location':'real_root memberships unknown_kinds provenance inventory',
'domain':'kind label parent provenance','copy':'version_id real_path location_id sha256 observation access status','statement':'text given_in class','case':'scope_id request status opened_in',
'check-card':'doubt decision operation outcomes cost budget_left','observation':'check_card agent delegation state result coverage observed_at class',
'claim':'kind subject statement class supports contradicts depends_on status','hypothesis':'subject text status for against next_check','open-item':'subject reason needed_to_resolve',
'finding':'source quote kind action_taken','map':'subject scenario verdict members evidence_level unknowns',
'plan':'case_id revision reference target_set recovery_folder goal preconditions success_conditions risks pending previous_receipt supersedes_plan',
'plan-entry':'plan_id asset_id name version_id expected_sha256 size_bytes source_path destination_path','approval':'plan_id plan_sha256 decision statement',
'receipt':'plan_id plan_sha256 overall reference set_complete coverage pending reason','receipt-entry':'receipt_id entry_id asset_id version_id status destination_path source_sha256_before destination_sha256 source_sha256_after note',
'test-case':'kind split facts expected source','policy':'version status condition scope effect motivated_by drafted_from rule_sha256 approval','evaluation':'policy_id rule_sha256 cases verdict','index-entry':'file bundle_id sha256 status'}
for rid, r in recs.items():
    t = r.get('type')
    if t not in req: print('UNKNOWN TYPE', rid, t); continue
    miss = [f for f in req[t].split() if f not in r]
    if miss: print('MISSING', rid, miss)
print('checked', len(recs))
