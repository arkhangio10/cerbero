# Scratch notes CAS-0002 (not a report)
Budget: digests 300, listings 60, 2GB.
Used: D3 listing x1 ; D7 digests x2 (memory files)
D1 user_home=/volume1/studio ; D2 says /volume1/studio not found (contradiction)
D2: aurora-2026-10-01 exists readable but NO real_path returned.
Memory: B-0001-01 digest 0589...4c0d matches IDX-0001-01. IDX digest d48d...f41b.
CHK-0002-0001: doubt: are the 11 recorded assets present with recorded size/time? decision: which need D7 and which need search; op: D5 file-agent; outcomes: missing->search; differ->D7; same->D7 for critical/set members; cost: metadata 11 paths read-only; budget_left: 298 digests, 59 listings
OBS D5#1: brief/copy/cover/preview/fonts/logo/palette present, size+mtime equal to records; layout.indd not_found; raw/DSC_0101,0142,0150 permission_denied.
CHK-0002-0002: doubt: are present critical set members brief.pdf, copy.docx, cover.tif, logo.ai still the Delivery 2 versions? decision: whether any member besides layout.indd needs recovery; op: D7 file-agent with expected digests VER-0001-0001/0002/0003/0007; outcomes: match->intact; differ->altered (add to recovery); cost: 4 digests, 51200 bytes, read-only; budget_left: 298 digests, 59 listings
OBS D7#2: brief, copy, cover, logo all match Delivery 2 digests -> intact. (6 digests used total)
CHK-0002-0003: doubt: was layout.indd moved/renamed inside the project (a 16384-byte file elsewhere in scope)? decision: moved (no copy needed) vs absent (recover); op: D6 file-agent on project root, size exactly 16384; outcomes: candidates->D7 vs VER-0001-0006; none + complete listing->absent in scope; cost: 1 listing, read-only; budget_left: 294 digests, 59 listings
OBS D6#1: project size=16384 -> empty, truncated=false, unreadable_subfolders=[.../aurora/raw] => possibly incomplete (rule 7).
CHK-0002-0004: doubt: which parts of the project search are incomplete, and can raw/ be searched separately? decision: whether relocation hypothesis can be closed; op: D13 file-agent on project root; outcomes: raw readable->D6 in raw; unreadable->record not reviewed; cost: 1 listing; budget_left: 294 digests, 58 listings
OBS D13#1: subfolders exports, raw; truncated=false; unreadable=[] (contradicts D6 which named raw unreadable)
CHK-0002-0005: doubt: is a 16384-byte file inside raw/ (or exports/)? decision: close or keep relocation hypothesis; op: D6 in raw, D6 in exports; outcomes: candidates->D7; empty+complete->not relocated in scope; cost: 2 listings; budget_left: 294 digests, 57 listings
OBS D6#2 raw: FAILED permission_denied -> raw/ not reviewed. OBS D6#3 exports: empty, complete.
=> layout.indd: missing at its path; in-scope search incomplete (raw/ unreadable).
Recorded copies of VER-0001-0006: CPY-0001-0006 (project path, now not_found), CPY-0001-0015 (backups/aurora-2026-10-01, root unresolved).
CHK-0002-0006: doubt: real path of backups/aurora-2026-10-01 (first D2 completed without real_path)? decision: whether CPY-0001-0015 can be re-checked as source; op: D2 file-agent, 1 folder; outcomes: canonical real path -> authorized root; none -> location unusable, search other locations; cost: metadata, read-only; budget_left: 294 digests, 55 listings
OBS D2#2: aurora-2026-10-01 again exists/readable, NO real_path -> containment unknown; CPY-0001-0015 not read (rule 12). Open item.
CHK-0002-0007: doubt: is there a 16384-byte file (possible VER-0001-0006) in backups/aurora-2026-11-05 or usb-archive/aurora? decision: which source, if any, can serve layout.indd Delivery 2; op: D6 file-agent x2, size exactly 16384; outcomes: candidates->D5/D7 vs 84a4...e1b; empty+complete->no copy there; cost: 2 listings; budget_left: 294 digests, 54 listings
OBS D6#4 11-05 size 16384: empty, complete. OBS D6#5 usb size 16384: empty, complete.
=> no eligible source for VER-0001-0006. Only remaining recorded copy CPY-0001-0015 unreachable (root unresolved).
Listings used: D3, D6 x5, D13 x1 = 7 (+ D2 x2 metadata). Digests used: 6.
Next: waiting_user choice (protocol step 4).
ask-user #1 reply: "Recover the available members of the target set as a partial recovery."
=> layout.indd is the only member needing recovery and has no eligible source -> partial recovery has 0 executable entries.
Decision: no plan (no plan-entry possible without source_path), no D11, no D12. Save case bundle B-0002-01 + IDX-0002-01. Receipt shown in report only (receipt record requires plan_id).
Bundle B-0002-01 composed: 50 records, 20097 bytes (scratch_B-0002-01.md).
D10 B-0002-01 APV-1 granted: /volume1/studio/cerbero-memory/CERBERO-B-0002-01.md verified 20097 bytes
D7 B-0002-01: a1b65aa09645f1437acdfbf55b38b56d6e2a9beee095d4f781f2ecd0d41ac168 20097
