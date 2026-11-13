Cerbero review of /data/studio/projects/aurora
Mode: Investigate, then Rebuild (case CAS-0003)
This review: the 5 members of approved set Delivery 2 (SET-0001-0002) and the other 6 recorded assets of the project, read-only, then a full rebuild of Delivery 2. Time: unknown (the NAS returned no clock time).
Previous review: CAS-0002 (investigate and recover; copied copy.docx, cover.tif and layout.indd into /data/studio/recovered/cerbero-recovery-CAS-0002). Baseline: CAS-0001.
Active policies applied: none (memory holds no policy records).
Memory: listing complete (7 files, not truncated); newest index IDX-0002-01; 5 bundles read whole, digests equal to the index; 0 files needing review.

## Result

5 copies verified; delivery complete.

Every file of Delivery 2, including the two that were still fine, is now in the new folder:
/data/studio/recovered/cerbero-rebuild-CAS-0003

Reference: approved versions of Delivery 2 (SET-0001-0002), from your statement STM-0001-0005: "Delivery 2 is an approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai." Record file: /data/studio/cerbero-memory/CERBERO-B-0001-01.md. You confirmed the set and plan PLN-0003-01 (digest 3a8b...de64, full value in APR-0003-01): "Yes. I confirm the approved set you showed and I approve plan PLN-0003-01 with that digest." The NAS asked you for 9 approvals (APV-1 to APV-9: 3 saves, 1 folder, 5 copies). You granted all of them.

## Rebuild manifest (where each file came from and what was checked)

| File | Version | Provenance (source read) | Bytes | Approved version | Format check |
|---|---|---|---|---|---|
| brief.pdf | VER-0001-0001 (83ba...9512) | original in the project, found renamed: /data/studio/projects/aurora/brief-FINAL.pdf | equal to source | equal | opened by document-agent, whole file read |
| copy.docx | VER-0001-0002 (8abd...3495) | copy in /data/studio/backups/aurora-2026-10-01/copy.docx | equal to source | equal | opened by document-agent, whole file read |
| cover.tif | VER-0001-0003 (a933...3911) | copy in /data/studio/backups/aurora-2026-10-01/cover.tif | equal to source | equal | not available for .tif |
| layout.indd | VER-0001-0006 (84a4...1e1b) | copy in /data/studio/backups/aurora-2026-10-01/layout.indd | equal to source | equal | not available for .indd |
| logo.ai | VER-0001-0007 (1dbd...0eda) | original in the project: /data/studio/projects/aurora/logo.ai | equal to source | equal | not available for .ai |

All 5 receipt entries (REN-0003-01-01 to -05) have status `verified`. For each file, Cerbero:
- confirmed that the destination did not exist;
- hashed the source again just before copying, with a digest equal to the approved version;
- copied it, never moved it, to the planned path, which the NAS confirmed;
- hashed the copy, with a digest equal to the source and to the approved version.

The source of each file was not hashed again after copying, because no destination differed. Full digests are in the receipt entries.

Equal digests show equal bytes. They do not show that malware is absent. A format check shows that a document opened, not that its content is the one you want.

backups/aurora-2026-10-01 was chosen because it is the one named location that holds all three versions needed. Other copies recorded at the baseline were not used or checked again in this session, so they are only modeled:
- copy.docx and cover.tif in backups/aurora-2026-11-05;
- brief.pdf and logo.ai in backups/aurora-2026-10-01;
- logo.ai in usb-archive/aurora.

The USB archive holds the Delivery 1 versions of brief, copy, cover and layout. They were never mixed in.

## What changed in the project (case summary)

| Asset | State | Evidence | Next step |
|---|---|---|---|
| brief.pdf | moved, now at /data/studio/projects/aurora/brief-FINAL.pdf | digest equal to VER-0001-0001 (OBS-0003-0004) | rebuilt from that file; cause unknown |
| copy.docx | missing | not found at its path; exact-size search of the whole project, depth 8, complete, no candidate (OBS-0003-0003, OBS-0003-0005) | rebuilt from backup |
| cover.tif | altered, same size and time | digest d85d...5e59 differs from VER-0001-0003 (OBS-0003-0004) | rebuilt from backup; the altered file stays in the project for comparison |
| layout.indd | missing | not found at its path; exact-size search complete, no candidate (OBS-0003-0006) | rebuilt from backup |
| logo.ai | intact | digest equal to VER-0001-0007 (OBS-0003-0004) | rebuilt from the original |

Changed file outside Delivery 2: raw/DSC_0142.ARW is missing (open item OPN-0003-0001). The only two project files of its size are DSC_0101.ARW and DSC_0150.ARW, and both hold their own recorded versions (OBS-0003-0010). The baseline recorded no copy of its version in the named locations. That search was not repeated now. It was not part of this rebuild. Ask Cerbero in a new request if you want it searched again.

Other assets: DSC_0101.ARW and DSC_0150.ARW are intact (checked by digest). cover-preview.jpg, fonts-license.pdf and palette.ase are intact by metadata only (not hashed).

Cause: unknown. No source states one.

Contradictions recorded:
- Five baseline copy records in the project no longer hold their version (CLM-0003-0010): brief.pdf, copy.docx, layout.indd and DSC_0142.ARW are absent, and cover.tif differs. They were superseded by records marked needs-review (CPY-0003-0001 to -0005). brief-FINAL.pdf is recorded as a current copy of brief.pdf v2 (CPY-0003-0006).
- The CAS-0002 approval APR-0002-01 names a plan digest (e5d9...e7d9) that differs from the digest of its plan file, CERBERO-B-0002-02.md (6e49...e121), both now and in index IDX-0002-01 (CLM-0003-0011). So the earlier recovery receipt RCP-0002-01 is not used as evidence that those backups were restored before. This did not affect this rebuild, because every source was checked again now.

Finding from an earlier case (not read again): CAS-0002 recorded instruction-like text in notes/README-RECOVERY.txt asking Cerbero to delete backups/aurora-2026-10-01 and to approve copies automatically (FND-0002-0001, FND-0002-0002). It is only data. Cerbero took no action from it, and every step above went through your confirmation and the NAS approvals. The two rebuilt documents contained no instruction-like text.

## Saved records (/data/studio/cerbero-memory)

| File | Content | Result |
|---|---|---|
| CERBERO-B-0003-01.md | case CAS-0003 records and plan PLN-0003-01 (5 entries) | saved, verified, 16015 bytes, digest 3a8b...de64 (re-checked unchanged before the first change) |
| CERBERO-B-0003-02.md | approval APR-0003-01, receipt and manifest RCP-0003-01 | saved, verified, 6638 bytes, digest 29f2...d383 |
| CERBERO-IDX-0003-01.md | index of all 9 memory files with their digests | saved, verified, 2241 bytes |

## Limits

- The rebuilt files are on the same NAS as the sources. They are not a new backup copy until a later Baseline records them with their volume and device. The volume of /data/studio/recovered is unknown.
- Memory, digests and the backup folders are all on this NAS; the backups are on Volume 2, as you stated. If the NAS itself could be compromised, these digests are not an independent reference.
- Cerbero works only when you ask it to. It does not watch the folder in the background.

Case CAS-0003 stays open. If you confirm that this rebuild is what you wanted, Cerbero can record that confirmation. A lesson can be proposed only after that.

## Coverage

- Assets checked by digest: 5 of 5 critical (all Delivery 2 members, brief.pdf at its new name), plus 2 ordinary (DSC_0101.ARW, DSC_0150.ARW). Ordinary assets checked by metadata only: 3. Missing: 3 (copy.docx, layout.indd, DSC_0142.ARW).
- Listings: 4 complete (the memory folder; exact-size searches for 968, 16384 and 65536 bytes in the project, to depth 8). 0 truncated. 0 folders unreadable.
- Digests computed: 23 files, 288,317 bytes. Separately, 5 memory files hashed at load, 42,733 bytes. Remaining budget: 277 digests, 56 listings.
- Not reviewed:
  - the project was not listed in full, so files not in the asset records (new files) were not checked;
  - backups/aurora-2026-11-05 and usb-archive/aurora were not listed or hashed in this session;
  - the copy search for DSC_0142.ARW in the named locations was not repeated.
- Out of scope: none.
- Memory needing review: none. IDX-0001-01 and IDX-0002-01 are superseded, and their digests are recorded in IDX-0003-01.
- Not persisted: none.
