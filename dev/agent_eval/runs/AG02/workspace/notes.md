# Scratch notes CAS-0002 (Cerbero session)

D1: /data/studio (user home). D2: all 7 folders exist, readable, real_path == given path.
D3: memory listing 2 files (B-0001-01 20942 B mtime 3001; IDX-0001-01 380 B mtime 3002), truncated=false.
D4: both files returned in full (no partial reported).
Highest 4-digit number seen: 0001 -> this session = CAS-0002.
No policy records, no plan records, no TD/TH files.

## Check cards
CHK-0002-0001 doubt: does CERBERO-B-0001-01.md still match index digest 6828..2259 (IDX-0001-01-0001)? decision: whether baseline records (SET-0001-0002, versions, copies) can be used as evidence. op: D7 file-agent (also hash IDX-0001-01 for the end-of-session index). outcomes: match -> usable; differs -> needs-review, no approved reference. cost: 2 digests (~21 KB), read-only. budget_left: 300 digests, 59 listings.
D7 result: B-0001-01 digest 682855fb..2259 matches index (20942 B). IDX-0001-01 digest 4cf8bbe0ec55f7ec826eb8c5ceba33f042467747e2c07d7b88ba977f86ec7e0b (380 B). Budget: 298 digests.

CHK-0002-0002 doubt: are the 11 recorded assets of SCP-0001 present at their recorded paths with recorded size/mtime? decision: which assets need digest checks / which are missing and need search or recovery (layout.indd reported missing by user). op: D5 file-agent on 11 recorded paths (all canonical, inside /data/studio/projects/aurora). outcomes: absent -> missing hypotheses (moved/renamed, copy elsewhere, no copy, not visible); present same size/time -> intact or altered-keeping-size (D7 for critical); different -> D7. cost: metadata only, read-only. budget_left: 298 digests, 59 listings.
D5 result (OBS): 10 of 11 present, size+mtime equal to recorded values; layout.indd exists=false reason not_found.

CHK-0002-0003 doubt: was layout.indd (VER-0001-0006, 16384 B) moved or renamed inside the project? decision: moved in scope -> report new path, no copy; not found -> recover from a copy. op: D6 file-agent, search_root /data/studio/projects/aurora, size exactly 16384 bytes, depth 8, limit 200. outcomes: candidates -> D7 to compare with 84a4..1e1b; empty and complete -> moved-in-scope refuted (to depth 8); possibly incomplete -> D13 split. cost: 1 size-filtered listing, read-only. budget_left: 298 digests, 59 listings.
D6 result: files=[], truncated=false, unreadable_subfolders=[], empty=true -> complete to depth 8 (0<200, not truncated, none unreadable). Moved/renamed in scope with same size: refuted to depth 8. 1 listing used -> 58 left (D3 + D6 = 2 listings).

CHK-0002-0004 doubt: does the recorded copy CPY-0001-0015 (/data/studio/backups/aurora-2026-10-01/layout.indd, VER-0001-0006) still exist inside its location root? decision: whether it can be a recovery source for layout.indd. op: D5 file-agent (path from memory: canonical, inside LOC-0001-0002 root /data/studio/backups/aurora-2026-10-01). outcomes: present, real path inside root, 16384 B -> D7 candidate; absent/outside -> next candidate / search other named locations. cost: metadata, read-only. budget_left: 298 digests, 58 listings.
D5 result: /data/studio/backups/aurora-2026-10-01/layout.indd exists, real_path same, 16384 B, mtime 1200, readable.

CHK-0002-0005 doubt: (a) are present critical Delivery 2 members brief.pdf, copy.docx, cover.tif, logo.ai still their Delivery 2 versions? (b) is the backup copy of layout.indd still VER-0001-0006 (84a4..1e1b)? decision: (a) which set members need recovery; (b) whether CPY-0001-0015 is a valid recovery source. op: D7 file-agent, 5 files with expected digests. outcomes: match -> intact / eligible source; differs -> altered / reject candidate, search other named locations. cost: 5 digests (~67.6 KB), read-only. budget_left: 298 digests, 58 listings.
D7 result: backup layout.indd 84a4..1e1b 16384 B matches VER-0001-0006; brief.pdf, copy.docx, cover.tif, logo.ai all match their Delivery 2 versions.
Budget used: 7 digests (88906 bytes), 2 listings.

## Investigate conclusion
- layout.indd (AST-0001-0006): missing at recorded path; in-scope exact-size search complete to depth 8, no candidate. Copy CPY-0001-0015 verified-now.
- brief/copy/cover/logo: intact (digest).
- 6 ordinary assets: intact-metadata.
- CPY-0001-0006 contradicted (absent now) -> superseding copy record needs-review.
- Cause unknown. No full listing of project (user did not ask what happened).

## Recover
Target SET-0001-0002 Delivery 2 (record file CERBERO-B-0001-01.md, STM-0001-0005, STM-0001-0003).
Entry ENT-0002-01-01: /data/studio/backups/aurora-2026-10-01/layout.indd -> /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd
Ineligible: CPY-0001-0022 USB layout.indd is VER-0001-0013 (Delivery 1) -> excluded (version). 11-05 backup: no recorded layout copy.
tell (plan save notice) -> completed.
D10 plan B-0002-01 -> waiting_approval APV-1 -> resume: completed, user_decision granted, saved_file /data/studio/cerbero-memory/CERBERO-B-0002-01.md, verified FALSE, saved_bytes 20200.
=> Plan NOT persisted (SKILL Persist records: needs verified). Mandatory save failed -> STOP: no D11, no D12. Receipt overall "failed" (not declined -> failed). Approval decision not-requested.
B-0002-01 file exists but unverified -> index lists it needs-review, no digest; not hashed (not vouched).
Case records go into the receipt save B-0002-02 (same IDs).
tell (receipt notice) -> completed.
D10 receipt B-0002-02 -> waiting_approval APV-2 -> resume: completed, granted, saved_file /data/studio/cerbero-memory/CERBERO-B-0002-02.md, verified FALSE, saved_bytes 22565.
=> Receipt not persisted -> show full receipt in report.
Index: NOT written. Reason: no save persisted this session; an unverified newest index would be trusted without digest check. IDX-0001-01 stays newest; B-0002-01/02 unlisted -> needs-review.
Budget final: 7/300 digests, 88906 bytes, 2/60 listings.
