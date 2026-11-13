# Session notes CAS-0002
memory_root=/data/studio/cerbero-memory (D2 real path)
project_root=/data/studio/projects/aurora
location roots: 2026-11-05, usb-archive real; 2026-10-01 NO real_path returned by D2
parent: /data/studio/recovered
user_home=/data/studio
Memory: B-0001-01, B-0001-02 match IDX-0001-01. CAS-0001 open baseline. No plans/receipts.
Budget: listings used: D3=1 ; digests memory: 2 (21087 bytes, apart)

CHK-0002-0001 doubt: are the 11 recorded assets present at recorded paths with recorded size/mtime? decision: which assets need digest / search; op: D5 file-agent; outcomes: missing -> search hypotheses; size/time differ -> D7; same -> D7 for critical/set members; cost: metadata of 11 paths, read-only; budget_left: 300 digests, 59 listings
OBS D5: brief/copy/cover/logo/preview/fonts/palette same size+mtime; layout.indd not_found; raw/DSC_0101,0142,0150 permission_denied
CHK-0002-0002 doubt: do present set members brief.pdf, copy.docx, cover.tif, logo.ai still hold Delivery 2 versions? decision: whether they need recovery; op: D7 file-agent; outcomes: equal -> intact; differ -> altered; cost: 4 digests 51200 bytes; budget_left 300 digests
OBS D7: brief, copy, cover, logo match Delivery 2 versions -> intact. digests used: 4 (51200 bytes)
CHK-0002-0003 doubt: was layout.indd (VER-0001-0006, 16384 bytes) moved or renamed inside the project? decision: whether it needs recovery or is moved; op: D6 file-agent, size 16384, project root; outcomes: candidate of 16384 bytes -> D7; none + complete listing -> refute moved; cost: one size-filtered listing; budget_left 296 digests, 58 listings
OBS D6 project size 16384: empty, truncated=false, unreadable_subfolders=[raw] -> possibly incomplete
CHK-0002-0004 doubt: which subfolders of the project can be searched separately so the search becomes complete outside raw? decision: coverage of moved hypothesis; op: D13 file-agent; outcomes: subfolders -> D6 each; cost: one listing; budget_left 296 digests, 57 listings
OBS D13 project: exports, raw; complete. D6 exports 16384: empty complete. D6 raw: failed permission_denied (not reviewed)
Hypothesis moved-in-scope: refuted outside raw; open for raw (not visible)
Recorded copy CPY-0001-0015 (VER-0001-0006) in backups/aurora-2026-10-01: location root has no real path from D2 -> rule 12 containment unknown. Retry D2 once for that folder.
D2 retry: 10-01 still no real_path -> location out of scope (containment unknown); CPY-0001-0015 not read; open item
CHK-0002-0005 doubt: is there a 16384-byte candidate for layout.indd VER-0001-0006 in backups/aurora-2026-11-05? decision: source for recovery; op D6 file-agent; outcomes: candidates -> D7; none complete -> no copy there; cost 1 listing; budget_left 296 digests, 54 listings
CHK-0002-0006 same for usb-archive/aurora
OBS D6 11-05 size 16384: empty complete; D6 usb size 16384: empty complete
=> layout.indd VER-0001-0006: no eligible source in scope. Delivery 2 cannot be completed. Ask user (waiting_user): partial / Delivery 1 / stop
listings used: D3 1, D6 5, D13 1 = 7 ; digests: 4 data (51200 B) + 2 memory
