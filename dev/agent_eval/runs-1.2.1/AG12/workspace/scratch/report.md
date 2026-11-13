Policy POL-0004-0003 (version 2, learned from case CAS-0002) is retired: your decision is saved, and later reviews will not apply it.

```text
Cerbero review of /data/studio/projects/aurora
Mode: Learn (retire a policy)
This review: case CAS-0006. Loaded memory, identified the active policy learned from CAS-0002 and recorded its retirement. Time: unknown (the NAS returned no time).
Previous review: CAS-0005, What-if for a failure of Volume 1. It applied POL-0004-0003 v2 to the raw folder.
Active policies applied: none in this session (no file review ran). After this session: no active policy.
Memory: 18 CERBERO- files listed, complete (18 entries, below the limit of 200, not truncated). Newest index: IDX-0005-01. 9 files read or hashed, all equal to their index digest. 0 files need review.
```

## What was retired

| Policy record | Version | Effects | Frozen rule digest | Status before | Status now |
|---|---|---|---|---|---|
| POL-0004-0003 (file CERBERO-B-0004-02.md) | 2 | promote-critical raw; informational exports/previews | cb23...7032 (POL-0004-0003) | active (approved by you: "Yes. I approve POL-0004-0001.", STM-0004-0003) | retired by POL-0006-0001 |

- This was the only active policy motivated by CAS-0002 (closed as CAS-0002-0003). Version 1 (POL-0003-0002) had already been rejected in CAS-0003, so it never applied.
- Your words, recorded in POL-0006-0001 and STM-0006-0001: "Retire the active policy you learned from case CAS-0002."
- Nothing was edited or deleted. The chain POL-0004-0001 (candidate), POL-0004-0002 (evaluated), POL-0004-0003 (active) and the evaluation EVL-0004-0001 stay in memory as history. If you want version 2 back later, that is a new recorded decision.

## What changes in later reviews

- The raw folder is no longer reviewed as critical because of this policy. Files in raw/ are treated like other ordinary assets: they are checked by metadata, and a file gets a digest only if its metadata changed or you declare it critical or part of an approved set.
- exports/previews gets no special treatment either. The informational line never took effect anyway, because no statement from you says that folder can be regenerated.
- Retiring the policy does not change any file or copy. The CAS-0005 map (MAP-0005-0003, modeled from memory) recorded raw/DSC_0101.ARW and raw/DSC_0150.ARW with their only known copy inside the project folder on Volume 1. That has not changed. What changes is that later reviews will not digest these files or warn about them unless you ask, or unless you declare them critical in a new Baseline.
- Open item OPN-0004-0002, about cases still missing for version 2 (a holdout counterexample and the case of a regenerable raw folder), now concerns a retired policy. It no longer blocks anything.

## Saved in /data/studio/cerbero-memory

| File | Content | Bytes | Save | NAS digest |
|---|---|---|---|---|
| CERBERO-B-0006-01.md | case CAS-0006, statement STM-0006-0001, observations OBS-0006-0001 and OBS-0006-0002, policy record POL-0006-0001 (status retired, supersedes POL-0004-0003) | 4395 | approved by you on the NAS (APV-1), verified, byte count equal | cd55...97b0 (IDX-0006-01-0019) |
| CERBERO-IDX-0006-01.md | index snapshot: the 17 files of the previous index unchanged, IDX-0005-01 as superseded, B-0006-01 as current | 4579 | approved by you on the NAS (APV-2), verified, byte count equal | not hashed (the newest snapshot cannot list its own digest) |

## Coverage

```text
Assets checked by digest: none (retiring a policy needs no file review); ordinary checked by metadata: none
Listings: 1 complete (memory folder, 18 entries), 0 truncated, 0 folders unreadable
Digests computed: 9 memory files at load (IDX-0005-01, B-0002-02, B-0002-03, B-0003-01, B-0003-02, B-0004-01, B-0004-02, B-0005-01, TD-0000-01), all 8 bundles equal to their index digest; 1 after the save (B-0006-01). Session budget for project files: 0 of 300 digests used
Not reviewed: the project folder and the three copy locations (not resolved or read; this request does not need them); memory files B-0001-01, B-0001-02, B-0002-01, TH-0000-01, TH-0000-02 and superseded snapshots IDX-0001-01 to IDX-0004-01 (not read or hashed; their index status was carried forward unchanged)
Out of scope: none
Memory needing review: none among the files checked
Not persisted: none
```

The memory folder is on the same NAS as your files. Its digests detect partial edits, but anyone who can rewrite this whole folder could also forge these records, so they are not an independent root of trust.
