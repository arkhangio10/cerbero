Cerbero review of /data/studio/projects/aurora
Mode: Investigate, then Recover (Delivery 2)
This review: case CAS-0002. The 11 recorded assets of the project, the copy of layout.indd in /data/studio/backups/aurora-2026-10-01, and the memory folder. Run time: unknown (the NAS returned no clock time).
Previous review: CAS-0001 (baseline, still open). It recorded 11 assets, 4 locations and approved sets Delivery 1 and Delivery 2. All its location inventories were recorded as complete.
Active policies applied: none (memory holds no policy records).
Memory: CERBERO-B-0001-01 and CERBERO-B-0001-02 are current. Their digests match the newest index CERBERO-IDX-0001-01. The memory listing was complete (3 files, not truncated). This session added CERBERO-B-0002-01, CERBERO-B-0002-02 and CERBERO-IDX-0002-01.

## What happened (case summary)

| Asset | State | Evidence | Next step |
|---|---|---|---|
| brief.pdf (Delivery 2) | moved. It is now at /data/studio/projects/aurora/old/2026/brief-final.pdf | Not found at its recorded path (OBS-0002-0001). The new path has a digest equal to Delivery 2 version VER-0001-0001, 9d2c...9055 (OBS-0002-0007) | None needed. The approved version is still in the project under another name. Cause unknown. |
| layout.indd (Delivery 2) | missing | Not found at its recorded path (OBS-0002-0001). No 16384-byte file in the readable part of the project (OBS-0002-0006) | Recovery was planned from the backup and you declined the plan. It stays missing. |
| copy.docx (Delivery 2) | intact | Digest equal to VER-0001-0002, 0745...03c4 (OBS-0002-0002) | none |
| cover.tif (Delivery 2) | intact | Digest equal to VER-0001-0003, 2c36...40ef (OBS-0002-0002) | none |
| logo.ai (Delivery 2) | intact | Digest equal to VER-0001-0007, 1dbd...0eda (OBS-0002-0002) | none |
| exports/previews/cover-preview.jpg | intact-metadata | Same size and time as recorded. Not hashed (OBS-0002-0001) | none |
| fonts-license.pdf | intact-metadata | Same size and time as recorded. Not hashed | none |
| palette.ase | intact-metadata | Same size and time as recorded. Not hashed | none |
| raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW | unknown | permission_denied. The folder raw/ is unreadable (OBS-0002-0001, OBS-0002-0003) | Restore read access to raw/, then check them again |

Recoverable source for layout.indd: /data/studio/backups/aurora-2026-10-01/layout.indd. In this session D5 confirmed its real path and D7 found its digest equal to VER-0001-0006, 84a4...1e1b (OBS-0002-0009, OBS-0002-0010). Evidence level: verified-now.

Open hypotheses:
- HYP-0002-0001: layout.indd was moved or renamed inside the project (open). The only part not searched is raw/, which is unreadable. To resolve it, restore read access to raw/ and run an exact-size search for 16384 bytes there.
- HYP-0002-0002: layout.indd is absent from the project with a copy elsewhere (supported, OBS-0002-0010).

Contradictions: memory recorded copies of brief.pdf and layout.indd at their project paths (CPY-0001-0001, CPY-0001-0006). Both paths are now not_found (CLM-0002-0012). Those copy records are superseded by needs-review records CPY-0002-0002 and CPY-0002-0003. The new location of brief.pdf is recorded as CPY-0002-0001.
Findings from documents: none. No document was read.
Cause: unknown. No source states why brief.pdf was moved to old/2026/brief-final.pdf or why layout.indd is absent. Modification times do not show who made a change or when.

## Recovery plan (not executed)

| Entry | Asset | Expected version | Source (re-observed) | Destination |
|---|---|---|---|---|
| ENT-0002-01-01 | layout.indd | VER-0001-0006, 84a4...1e1b | /data/studio/backups/aurora-2026-10-01/layout.indd | /data/studio/recovered/cerbero-recovery-CAS-0002/layout.indd |

Target: approved set SET-0001-0002 "Delivery 2". Record file: /data/studio/cerbero-memory/CERBERO-B-0001-01.md. Approving statement: STM-0001-0005.
Plan: PLN-0002-01, saved in /data/studio/cerbero-memory/CERBERO-B-0002-01.md. Saved digest: 7734e9642a958ae3b70b8629f59daebb92afd72a3621ad3b05da6add249f32f0.
Your decision: declined. Your words: "No. I do not approve plan PLN-0002-01. Do not create or copy anything." (APR-0002-0001, STM-0002-0002)

## Receipt RCP-0002-01

| Entry | File | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|---|
| ENT-0002-01-01 | layout.indd | cancelled | not run | not run | Plan declined. No folder was created and nothing was copied. |

Result of the copies: 0 copies verified. Overall status: cancelled.
Delivery: delivery incomplete. layout.indd is pending: it is missing from the project, and its recovery was cancelled. The other 4 members are satisfied: brief.pdf (moved, equal digest), copy.docx, cover.tif and logo.ai (intact).
Reference: approved versions of Delivery 2.
Changed files outside the requested target: raw/DSC_0101.ARW, raw/DSC_0142.ARW and raw/DSC_0150.ARW (state unknown, permission denied). Memory records no copy of their versions in the named locations. They were not searched in this session.
Nothing was created or changed in the project, the backups or /data/studio/recovered.
Receipt saved at /data/studio/cerbero-memory/CERBERO-B-0002-02.md (verified, 2304 bytes, digest 3cb3...dbb9).

To recover layout.indd later, ask again. Recovery would need a new plan revision with a new confirmation. The backup copy would be checked again before any copy.

## Coverage

Assets checked by digest: 4 of 5 critical Delivery 2 members, at their current paths (brief.pdf at its new path, plus copy.docx, cover.tif and logo.ai). layout.indd could not be hashed because it is missing. Ordinary assets checked by metadata only: 3. Ordinary assets not checked: 3 (raw, permission denied).
Listings (6 of 60):
- memory folder: complete;
- project, any size: truncated, raw unreadable;
- project subfolders: truncated;
- project, exactly 4096 bytes: not truncated, raw unreadable;
- project, exactly 16384 bytes: not truncated, raw unreadable;
- exports: complete.
Depth was 8 and the limit was 200 entries.
Digests computed: 7 files, 85776 bytes. That is 5 data files (67584 bytes) plus the 2 saved memory files. In addition, 3 memory files were hashed for the memory check and are counted apart.
Not reviewed:
- the contents of /data/studio/projects/aurora/raw;
- the parts of the project not returned by the truncated full listing (for example the rest of old/ and the files directly in the project root). New files or notes there cannot be ruled out;
- the backup folders /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. They were not needed: the recorded copy in aurora-2026-10-01 matched. The USB archive holds a Delivery 1 layout.indd version according to memory, and that version is never mixed into Delivery 2.

Out of scope: none.
Memory needing review: none.
Not persisted: none. The plan (B-0002-01), the receipt (B-0002-02) and the index snapshot (IDX-0002-01) were saved and verified. For B-0002-01 the NAS reported 15888 bytes. That is the bundle text without the final line break of the instruction file, and D7 confirmed the saved file is byte-identical to that text.

Limits: a matching digest shows equal content, not who changed a file, and not that malware is absent. Memory and copies live on the same NAS, so they are not an independent root of trust. This review is a one-time check, not continuous protection.
