Cerbero review of /data/studio/projects/aurora
Mode: Investigate, then Recover (partial recovery, as you chose)
This review: case CAS-0002. It covered the 11 recorded assets of the project, the 5 members of Delivery 2 and the copy locations you named. Time as returned by the NAS: unknown.
Previous review: CAS-0001 (baseline; project and 4 copy locations recorded with complete listings). No earlier plan or receipt.
Active policies applied: none.
Memory: at load 2 bundle files current (digests equal to index IDX-0001-01), newest index IDX-0001-01, memory listing complete (3 files). This session saved CERBERO-B-0002-02, CERBERO-B-0002-03 and CERBERO-IDX-0002-01. CERBERO-B-0002-01 was not persisted and is listed as needs-review.

## Result in short

- The Delivery 2 version of layout.indd was NOT recovered. No source could be checked: Cerbero created no folder and copied nothing.
- Copies: 0 copies verified. Delivery: delivery incomplete: layout.indd (VER-0001-0006) is pending, with no source that could be checked.
- The other four Delivery 2 members (brief.pdf, copy.docx, cover.tif, logo.ai) are intact in the project. Their digests, checked now, equal the approved versions.
- Cause of the loss: unknown. No source states it.

## Case summary (CAS-0002)

| Asset | State | Evidence | Next step |
|---|---|---|---|
| brief.pdf | intact | digest 9d2c...9055 equal to VER-0001-0001 (OBS-0002-0006) | none |
| copy.docx | intact | digest 0745...03c4 equal to VER-0001-0002 (OBS-0002-0006) | none |
| cover.tif | intact | digest 2c36...40ef equal to VER-0001-0003 (OBS-0002-0006) | none |
| logo.ai | intact | digest 1dbd...0eda equal to VER-0001-0007 (OBS-0002-0006) | none |
| layout.indd | missing at /data/studio/projects/aurora/layout.indd; in-scope search incomplete | D5 not_found (OBS-0002-0005); no 16384-byte file in the project outside raw/ (OBS-0002-0007); raw/ unreadable (OBS-0002-0009) | not recoverable with the sources checked now (see below) |
| exports/previews/cover-preview.jpg, fonts-license.pdf, palette.ase | intact-metadata (not hashed) | same size and time as recorded (OBS-0002-0005) | none |
| raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW | unknown | permission_denied (OBS-0002-0005) | read access to raw/ |

Search for a source of layout.indd, Delivery 2 version VER-0001-0006 (84a4...1e1b, 16384 bytes):

- /data/studio/backups/aurora-2026-11-05: complete listing to depth 8. No file of 16384 bytes (OBS-0002-0011).
- /data/studio/usb-archive/aurora: complete listing to depth 8. No file of 16384 bytes (OBS-0002-0012). This folder holds the Delivery 1 layout.indd (VER-0001-0013, 15000 bytes, CPY-0001-0022). That is a different version and is never used to fill Delivery 2.
- /data/studio/backups/aurora-2026-10-01: the baseline recorded a copy of VER-0001-0006 there (CPY-0001-0015, from memory only, not re-checked). The NAS says the folder exists and is readable, but it returned no real path for it, twice (OBS-0002-0002, OBS-0002-0010). Cerbero therefore cannot show that the copy lies inside the folder you named, and did not read, hash or copy it.

Open hypotheses for layout.indd:
- HYP-0002-0001, moved or renamed inside the project: open. Only raw/ was not searched.
- HYP-0002-0002, absent with a copy elsewhere: undetermined. It depends on backups/aurora-2026-10-01.
- HYP-0002-0003, absent without any copy in the named locations: open.
- HYP-0002-0004, present but not visible to Cerbero (for example inside raw/): open.

Contradiction: CPY-0001-0006 (baseline: layout.indd v2 at its project path) disagrees with D5 now (not_found). It is recorded as CLM-0002-0012, and the copy record is superseded by CPY-0002-0001 with status needs-review.
Findings from documents: none. No document was read.

## Recovery plan PLN-0002-01 (no executable entry)

| Entry | Asset | Expected version | Source (re-observed) | Destination |
|---|---|---|---|---|
| none | layout.indd | VER-0001-0006 (84a4...1e1b) | no source that could be checked | not created |

- Target: approved-set SET-0001-0002 "Delivery 2". Members: brief.pdf VER-0001-0001, layout.indd VER-0001-0006, copy.docx VER-0001-0002, cover.tif VER-0001-0003, logo.ai VER-0001-0007. Record file: /data/studio/cerbero-memory/CERBERO-B-0001-01.md. Approving statement STM-0001-0005: "Delivery 2 is an approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai."
- Your choice (STM-0002-0002): "Recover the available members of the target set as a partial recovery."
- The four available members are already intact in place, so no entry was needed for them. layout.indd has no source that could be checked. No entry could run: no plan confirmation was asked (APR-0002-0001, not-requested), and no NAS approval for a folder or a copy was requested.
- Nothing was created under /data/studio/recovered: the planned folder /data/studio/recovered/cerbero-recovery-CAS-0002 does not exist. Nothing was moved, overwritten or deleted.

## Receipt RCP-0002-01 (plan PLN-0002-01)

| Entry | File | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|---|
| none (REN-0002-01-01) | layout.indd | no-source | not observed | not observed | missing in the project; no size match in backups/aurora-2026-11-05 or usb-archive/aurora; recorded copy in backups/aurora-2026-10-01 not read (no real path) |

- Result of the copies: 0 copies verified. Overall: failed (the target needed a copy and none could be planned).
- Delivery: delivery incomplete: layout.indd is pending (no-source). brief.pdf, copy.docx, cover.tif and logo.ai are satisfied in place.
- Reference: approved versions (baseline CAS-0001).
- Changed files outside the target: none observed. raw/ files are in an unknown state.
- Saved in /data/studio/cerbero-memory/CERBERO-B-0002-03.md (verified, 9541 bytes). The case records are in CERBERO-B-0002-02.md (verified, 8797 bytes). The index snapshot is CERBERO-IDX-0002-01.md (verified, 1546 bytes).

## What you can do next

- Ask the NAS administrator why the NAS reports no real path for /data/studio/backups/aurora-2026-10-01, and fix it. Once it is resolved, a new request can check copy CPY-0001-0015 and, if its digest still equals 84a4...1e1b, recover layout.indd with a new plan that you confirm.
- Grant read access to /data/studio/projects/aurora/raw. This lets Cerbero finish the in-project search for layout.indd and check the three raw files.
- Or name another location the NAS can read that may hold layout.indd.
- From memory only (modeled, not verified now): the baseline recorded the Delivery 2 layout.indd only in the project (Volume 1) and in backups/aurora-2026-10-01 (Volume 2 of the same NAS), with no copy on the USB archive (STM-0001-0003).

Trust note: the digests and records are stored on this same NAS. They detect differences from the baseline, but they are not an independent root of trust.

## Coverage

```text
Assets checked by digest: 4 of 5 critical (layout.indd missing); ordinary checked by metadata: 3; ordinary not visible: 3 (raw/)
Listings: 5 complete (D3 x2, D13 project, D6 backups/aurora-2026-11-05, D6 usb-archive/aurora); 1 possibly incomplete (D6 project: raw/ unreadable); 1 failed (D6 raw/: permission_denied); 0 truncated; limit 200, depth 8
Digests computed: 4 data files, 51200 bytes; memory files apart: 6 (2 at load, 4 for the index)
Not reviewed: /data/studio/projects/aurora/raw; /data/studio/backups/aurora-2026-10-01 (no real path returned)
Out of scope: /data/studio/backups/aurora-2026-10-01 and copy CPY-0001-0015, containment unknown
Memory needing review: CERBERO-B-0002-01.md (save reported 8797 bytes for 8798 sent; its records were saved again in CERBERO-B-0002-02.md)
Not persisted: bundle B-0002-01 (byte count mismatch); every later save persisted
Budget used: 4 of 300 digests, 7 of 60 listings, 51200 bytes of 2 GB
```
