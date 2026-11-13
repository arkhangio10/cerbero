Nothing was created or copied: the Delivery 2 version of layout.indd has no source Cerbero could verify. The other four Delivery 2 files are intact in the project. Delivery incomplete: layout.indd is still missing.

```text
Cerbero review of /data/studio/projects/aurora
Mode: Investigate, then Recover (partial recovery of approved set Delivery 2, chosen by you)
This review: case CAS-0002. Covered the 11 recorded assets of the project, a size search for layout.indd in the project and in the copy locations the NAS could resolve, and the memory folder. Time: unknown (the NAS returned no clock time).
Previous review: CAS-0001 (baseline), recorded in CERBERO-B-0001-01 and CERBERO-B-0001-02
Active policies applied: none (no policy records in memory)
Memory: 3 files listed, complete listing. CERBERO-B-0001-01 and CERBERO-B-0001-02 match the newest index IDX-0001-01 (current). No file needs review. No unfinished plans.
```

## What changed (case summary)

| Asset | State | Evidence | Next step |
|---|---|---|---|
| layout.indd | missing at /data/studio/projects/aurora/layout.indd | D5 not_found (OBS-0002-0006); no 16384-byte file in the project outside raw (OBS-0002-0008, OBS-0002-0010) | recover VER-0001-0006 when a source becomes verifiable; cause unknown |
| brief.pdf | intact | digest 9d2c...9055 equal to Delivery 2 version VER-0001-0001 (OBS-0002-0007) | none |
| copy.docx | intact | digest 0745...03c4 equal to VER-0001-0002 (OBS-0002-0007) | none |
| cover.tif | intact | digest 2c36...40ef equal to VER-0001-0003 (OBS-0002-0007) | none |
| logo.ai | intact | digest 1dbd...0eda equal to VER-0001-0007 (OBS-0002-0007) | none |
| exports/previews/cover-preview.jpg, fonts-license.pdf, palette.ase | intact-metadata (size and time as recorded, not hashed) | OBS-0002-0006 | none |
| raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW | unknown: permission denied | OBS-0002-0006 | restore read access to the raw folder, then review again |

Open hypotheses for layout.indd:
- Moved or renamed inside the project (HYP-0002-0001): ruled out everywhere except the raw subfolder, which could not be read.
- Absent, with a copy elsewhere (HYP-0002-0002): undetermined. The only recorded copy of the Delivery 2 version is /data/studio/backups/aurora-2026-10-01/layout.indd (CPY-0001-0015, from the baseline). The NAS confirmed that folder exists but did not return its real path, twice, so Cerbero cannot show that the path stays inside it and did not read it.
- Absent without any copy (HYP-0002-0003): open.
- Present but not visible (HYP-0002-0004): open, because raw is unreadable.

Contradictions: none. No new observation contradicts a recorded digest.
Cause: unknown. No source states how layout.indd disappeared.

## Recovery

You chose: "Recover the available members of the target set as a partial recovery."

Target: approved set SET-0001-0002, Delivery 2, recorded in /data/studio/cerbero-memory/CERBERO-B-0001-01.md, from your statement STM-0001-0005: "Delivery 2 is an approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai." The only member that needed a copy was layout.indd, and it has no eligible source. So plan PLN-0002-01 has no entries. No plan confirmation was asked (APR-0002-01: not-requested). The recovery folder /data/studio/recovered/cerbero-recovery-CAS-0002 was not created.

| Entry | File | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|---|
| none (REN-0002-01-01) | layout.indd (VER-0001-0006, 84a4...1e1b) | no-source | not observed | not observed | the recorded copy is out of scope (no real path for its folder); no 16384-byte file in the resolved locations |

- Result of the copies: 0 copies verified. Receipt RCP-0002-01, overall `failed`: the target needed one copy and none could be planned.
- Delivery: incomplete. layout.indd is pending as no-source. brief.pdf, copy.docx, cover.tif and logo.ai are satisfied in place with matching digests.
- Reference: approved versions from the baseline.
- Files outside the target, reported apart: raw/DSC_0101.ARW, raw/DSC_0142.ARW and raw/DSC_0150.ARW, state unknown. The baseline recorded no copy of them in the named copy locations; this was not checked again.
- Saved: the receipt and the plan in /data/studio/cerbero-memory/CERBERO-B-0002-02.md (digest 1b60...088f), the case records in CERBERO-B-0002-01.md (52c4...e4d4), and the index snapshot in CERBERO-IDX-0002-01.md. All three saves were verified, with byte counts equal to the text sent.

Supported next steps:
- Find out why the NAS does not return a real path for /data/studio/backups/aurora-2026-10-01, or name another folder the NAS can read that may hold layout.indd. Then ask again, and Cerbero will check that copy with D5 and D7 before a new plan.
- Restore read access to /data/studio/projects/aurora/raw, so the move hypothesis and the three ARW files can be checked.
- /data/studio/usb-archive/aurora holds only the Delivery 1 version of layout.indd (VER-0001-0013). It is never used to fill a Delivery 2 gap.

## Coverage

```text
Assets checked by digest: 4 of 5 Delivery 2 members, all critical (layout.indd missing); ordinary checked by metadata: 3; ordinary not visible: 3 (raw)
Listings: 6 complete (memory; project subfolders; exports; backups/aurora-2026-11-05; usb-archive/aurora, size 16384, depth 8), 1 possibly incomplete (project root search: raw unreadable), 1 failed (raw: permission_denied); 7 of 60 used
Digests computed: 4 data files, 51200 bytes; memory digests counted apart: 5 files, 39778 bytes
Not reviewed: /data/studio/projects/aurora/raw (permission denied); full listing of the project for new or unrecorded files (not run: the request was to recover, not to explain what happened)
Out of scope: /data/studio/backups/aurora-2026-10-01 and everything in it, because D2 returned no real path (OPN-0002-0001)
Memory needing review: none
Not persisted: none
```

Limits: memory and digests are stored on the same NAS as the data. They detect differences from the baseline, but they are not an independent root of trust.
