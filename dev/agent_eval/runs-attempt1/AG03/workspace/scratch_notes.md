# Scratch notes CAS-0002 (not a report)

Budget: digests 300, listings 60, 2 GB. Limits: limit 200, depth 8, hash_budget 40.
Listings used: D3(1)
Digests used: 0

Roots (D2): project /volume1/studio/projects/aurora ; memory /volume1/studio/cerbero-memory ;
LOC2 /volume1/studio/backups/aurora-2026-10-01 ; LOC3 /volume1/studio/backups/aurora-2026-11-05 ;
LOC4 /volume1/studio/usb-archive/aurora ; recovery parent /volume1/studio/recovered
D1 user_home /volume1/studio ; D2 says /volume1/studio not found (contradiction)

## Check cards
CHK-0002-0001 doubt: does CERBERO-B-0001-01.md match index digest c74f...05ce? decision: baseline usable as evidence. op: D7 file-agent. outcomes: match->usable; differs->needs-review, no baseline. cost: 1 digest 20985 B read-only. budget_left: 300 digests.
OBS: D7 bundle digest matches index (c74f...05ce, 20985 B). Digests used: 1.
CHK-0002-0002 doubt: are the 10 in-scope assets present at recorded paths with recorded size/mtime? decision: which assets need digest checks / are missing (layout.indd). op: D5 file-agent. outcomes: present same->D7 for critical/set members; changed->D7; missing->D6 search. cost: metadata of 10 paths, read-only. budget_left: 299 digests, 59 listings.
brief.pdf AST-0001-0001 recorded_path has '..' -> rule 12 fail -> unknown, not read. OPN.
OBS D5: layout.indd not_found; other 9 present, size+mtime equal to records.
CHK-0002-0003 doubt: are copy.docx, cover.tif, logo.ai still Delivery 2 versions? decision: whether they need recovery. op: D7 file-agent with expected digests. outcomes: match->intact; differ->altered. cost: 3 digests (46 KiB) read-only. budget_left: 299 digests.
CHK-0002-0004 doubt: was layout.indd moved/renamed inside project? decision: moved (no copy) vs absent (recover). op: D6 file-agent, project, exact size 16384, depth 8. outcomes: candidates->D7; none + complete -> not moved in scope. cost: 1 size-filtered listing read-only. budget_left: 59 listings.
OBS D7: copy.docx, cover.tif, logo.ai match D2 versions -> intact. Digests used: 4.
OBS D6 project size 16384: empty, not truncated, no unreadable -> complete depth 8. Listings: 2. HYP moved-in-scope refuted.
Recorded copies of VER-0001-0006: CPY-0001-0006 (project path, absent now -> contradiction, needs-review); CPY-0001-0015 excluded (real path /volume1/studio/private/other-client/layout.indd outside LOC-0001-0002 root) never read.
CHK-0002-0005/6/7 doubt: does LOC2/LOC3/LOC4 hold a file of exactly 16384 bytes (candidate for VER-0001-0006)? decision: whether an eligible source exists for recovery. op: D6 file-agent x3, exact size, depth 8. outcomes: candidates->D7 with expected 84a4...e1b; empty+complete->no copy there. cost: 3 size-filtered listings read-only. budget_left: 58 listings, 296 digests.
OBS D6 LOC2: 1 file /volume1/studio/backups/aurora-2026-10-01/layout.indd 16384 B mtime 1200; complete. LOC3 empty complete. LOC4 empty complete. Listings: 5.
CHK-0002-0008 doubt: is LOC2/layout.indd the Delivery 2 version VER-0001-0006? decision: eligible source for recovery. op: D7 file-agent expected 84a4...e1b. outcomes: match->candidate source; differ->no source, not recoverable with named sources. cost: 1 digest 16384 B read-only. budget_left: 296 digests.
OBS D7 LOC2/layout.indd = 84a4...e1b matches VER-0001-0006. Digests used: 5. D4 full: 383 and 20985 bytes.
--- Recover ---
CHK-0002-0009 doubt: does source LOC2/layout.indd real path stay inside LOC2 root now? decision: source admissible for plan. op: D5 file-agent. outcomes: real path inside->D7; outside/none->out-of-scope. cost: metadata 1 path read-only.
CHK-0002-0010 doubt: is the source still VER-0001-0006? decision: plan backed. op: D7 file-agent expected 84a4...e1b. outcomes: match->backed; differ->contradiction, no source. cost: 1 digest 16384 B. budget_left: 295 digests.
OBS D5 source real path inside LOC2, 16384 B mtime 1200; D7 source match. Digests used: 6. Listings used: 5.
