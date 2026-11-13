# Scratch notes CAS-0002 (session case)
Roots resolved (D2): project /data/studio/projects/aurora ; memory /data/studio/cerbero-memory ; LOC2 /data/studio/backups/aurora-2026-10-01 ; LOC3 /data/studio/backups/aurora-2026-11-05 ; LOC4 /data/studio/usb-archive/aurora ; recovery parent /data/studio/recovered ; user_home /data/studio (not an authorized root)
Budget: digests 300, listings 60, 2GB. Used: listings D3=1 ; digests 0
Scope violations from memory: AST-0001-0001 recorded_path has '..' -> unknown, not read. CPY-0001-0015 real_path /data/studio/private/other-client/layout.indd outside LOC-0001-0002 root -> excluded, not read.

CHK-0002-0001 doubt: does bundle B-0001-01 still match its index digest? decision: whether baseline records are usable evidence. op: D7 file-agent on 1 memory file. outcomes: match -> current; differ -> needs-review, no baseline. cost: 1 digest of 20964 bytes, read-only. budget_left: 300 digests
OBS D7 memory: B-0001-01 digest 22d9...e19a matches index -> current. Bundle parses: 79 records, no errors, refs resolve. Digests used: 1

CHK-0002-0002 doubt: are the 10 in-scope assets present at their recorded paths with recorded size/mtime? decision: which assets need digest checks and which are missing (layout.indd per user). op: D5 file-agent on 10 recorded asset paths (AST-0001-0001 excluded: path not canonical). outcomes: present same size/time -> D7 for critical; changed -> D7; missing -> D6 exact-size search. cost: metadata only, read-only. budget_left: 299 digests, 59 listings
OBS D5 (CHK-0002-0002): 9 present, same size+mtime as recorded; layout.indd exists=false reason not_found.

CHK-0002-0003 doubt: are copy.docx, cover.tif, logo.ai at recorded paths still the Delivery 2 versions? decision: whether those set members need recovery (Delivery 2 completeness). op: D7 file-agent on 3 files with expected digests VER-0001-0002/0003/0007. outcomes: match -> intact; differ -> altered, recover. cost: 3 digests (46592 bytes), read-only. budget_left: 299 digests, 59 listings
OBS D7 (CHK-0002-0003): copy.docx, cover.tif, logo.ai match Delivery 2 digests -> intact. Digests used: 4

CHK-0002-0004 doubt: was layout.indd moved/renamed inside the project? decision: whether layout.indd v2 needs a copy from another location or is just at a new path. op: D6 file-agent under project root, size exactly 16384, depth 8, limit 200. outcomes: candidates -> D7 vs VER-0001-0006; none (complete) -> refute moved-in-scope, go to copy locations. cost: 1 size-filtered listing, read-only. budget_left: 296 digests, 59 listings
OBS D6 (CHK-0002-0004): project size=16384: empty, truncated=false, no unreadable -> complete to depth 8. Moved-in-scope refuted. Listings used: 2
Copy records VER-0001-0006: CPY-0001-0006 (project path, now not_found -> contradiction), CPY-0001-0015 (real_path outside LOC-0001-0002 root -> excluded, not read).

CHK-0002-0005 doubt: does any named copy location hold a 16384-byte file that could be layout.indd v2? decision: whether a source exists for recovery of VER-0001-0006. op: D6 file-agent x3 (LOC2, LOC3, LOC4) size exactly 16384, depth 8, limit 200. outcomes: candidates -> D7 vs VER-0001-0006; none in all (complete) -> no source, not recoverable with available sources. cost: 3 size-filtered listings, read-only. budget_left: 296 digests, 58 listings
OBS D6 (CHK-0002-0005): LOC2 1 file /data/studio/backups/aurora-2026-10-01/layout.indd 16384 mtime 1200, truncated=false, unreadable none -> complete; LOC3 empty complete; LOC4 empty complete. Listings used: 5

CHK-0002-0006 doubt: is /data/studio/backups/aurora-2026-10-01/layout.indd the Delivery 2 version VER-0001-0006? decision: whether it can be the recovery source. op: D7 file-agent, 1 file, expected 84a4...1e1b. outcomes: match -> eligible source (verified-now); differ -> no source for layout v2. cost: 1 digest 16384 bytes, read-only. budget_left: 296 digests, 55 listings
