# Session log (Cerbero What-if, project Aurora)

## Roots resolved (D2 completed)
- project_root: /data/studio/projects/aurora
- memory_root: /data/studio/cerbero-memory
- location_root A: /data/studio/backups/aurora-2026-10-01
- location_root B: /data/studio/backups/aurora-2026-11-05
- location_root C: /data/studio/usb-archive/aurora
- user_home (D1): /data/studio (not an authorized root)

## Check cards
CHK-a (D3): doubt "which Cerbero memory files exist?"; decision "whether a baseline/map exists to evaluate the volume scenario"; operation D3 file-agent; outcomes "empty: no baseline, offer Baseline; files: read index"; cost: 1 listing, read-only; budget_left: 60 listings, 300 digests
OBS D3 completed: 20 files, truncated false, no unreadable subfolder -> complete. Newest index CERBERO-IDX-0006-01.md. Case opened: CAS-0007.
CHK-b (D4): doubt "what files does the newest index list, with which digests and status?"; decision "which records are trusted for the What-if"; operation D4 file-agent on IDX-0006-01; outcomes "entries with digests -> verify records; missing parts -> needs-review"; cost: read 4579 bytes, read-only; budget_left: 59 listings, 300 digests
OBS D4 completed: IDX-0006-01 read whole; 19 entries; lists every D3 file except itself.
CHK-c (D4): doubt "which records hold the Aurora approved sets, versions, copies, locations, domains and policies?"; decision "inputs of the volume What-if"; operation D4 file-agent on 11 B- bundles; outcomes "records found -> verify digests vs index; none -> offer Baseline"; cost: read ~80 KB, read-only; budget_left: 59 listings, 300 digests
OBS D4 completed: 11 B- bundles returned whole (byte counts = D3 sizes). Local parse: 197 records valid; only unresolved refs are drafted_from TST-0000-0001/0002 (in TD-0000-01, not read) on policy records.
CHK-d (D7): doubt "do the 11 bundle files still match their index digests?"; decision "whether baseline, copies, sets, domains, receipt and policy records are trusted evidence"; operation D7 file-agent (memory load, counted apart); outcomes "equal: current; different: needs-review, stop using"; cost: 11 digests, 80370 bytes; budget_left: 300 digests (memory digests counted apart)
OBS D7 completed: 11/11 bundle digests equal index digests; real paths equal D3 real paths -> current/trusted. (memory digests: 11, 80370 bytes, counted apart)
Policy: newest record of chain = POL-0006-0001 status retired (supersedes POL-0004-0003 v2 active). No active policy -> none applied.
CHK-0007-0001 (D6): doubt "which files does the project folder hold now?"; decision "which current files a Volume 1 failure would reach, including files with no recorded version (no known copy) and recorded files no longer present"; operation D6 file-agent on /data/studio/projects/aurora, of any size, limit 200, depth 8; outcomes "complete listing: current file set known; possibly incomplete: split with D13; unrecorded file: no known copy; recorded path absent: confirms earlier contradiction"; cost: 1 listing, read-only; budget_left: 60 listings, 300 digests, 2 GB
OBS-D6 (CHK-0007-0001) completed: 9 files, truncated false, unreadable [] -> complete to depth 8. brief-FINAL.pdf 4096/1100; cover.tif 32768/1103; exports/previews/cover-preview.jpg 4096/1104; fonts-license.pdf 2048/900; logo.ai 8192/900; notes/README-RECOVERY.txt 237/2000; palette.ase 512/900; raw/DSC_0101.ARW 65536/800; raw/DSC_0150.ARW 65536/802. Absent: brief.pdf, copy.docx, layout.indd, raw/DSC_0142.ARW. Same as OBS-0005-0003.
ask-user (offer read-only verification of copies now): reply "I have nothing to add. Continue only with what you can verify, or stop." -> not a request to verify; no copy-folder reads; evidence stays modeled.
Eligibility (local reasoning over trusted records): see scratch/eval.py output. D2 all modeled recoverable; D1 modeled recoverable (4/5 only via USB, inferred outside); ordinary versions 0 eligible.
CHK-e (D7, memory): doubt "digest of IDX-0006-01"; decision "list it as superseded with a digest in IDX-0007-01"; cost 1 digest 4579 bytes (memory, counted apart)
tell: notice before save of B-0007-01. D10 B-0007-01 -> waiting_approval APV-1 -> resume: completed, verified, saved_bytes 11253 (= sent), path /data/studio/cerbero-memory/CERBERO-B-0007-01.md -> persisted.
