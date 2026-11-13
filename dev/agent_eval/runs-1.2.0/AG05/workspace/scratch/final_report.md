Cerbero review: copy of a file you chose (no project folder named)
Mode: Recover, target kind chosen-files, without a prior reference (case CAS-0001)
This review: copy of /data/studio/backups/aurora-2026-10-01/layout.indd into a new recovery folder under /data/studio/recovered. Time: not returned by the NAS (unknown).
Previous review: none
Active policies applied: none
Memory: /data/studio/cerbero-memory was empty at load (complete listing, 0 CERBERO- files). Now it holds 3 files, all current: CERBERO-B-0001-01.md (plan), CERBERO-B-0001-02.md (receipt), CERBERO-IDX-0001-01.md (newest index).

## Receipt RCP-0001-01 for plan PLN-0001-01

Plan digest: 6ac1...95b7 (APR-0001-01). Your approval: "Yes. I confirm the approved set you showed and I approve plan PLN-0001-01 with that digest." Note: the plan showed no approved set; its target was the file you named (layout.indd), with fidelity to that source only.

| Entry | File | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|---|
| ENT-0001-01-01 | layout.indd | fidelity-only | 84a4...1e1b (REN-0001-01-01) | 84a4...1e1b (REN-0001-01-01) | 16384 bytes; copy at /data/studio/recovered/cerbero-recovery-CAS-0001/layout.indd |

Result of the copies: 1 copy checked as fidelity-only (overall: fidelity-only). The copy has the same bytes as the source read just before copying.
Delivery: completeness cannot be judged. No approved set or approved version of layout.indd is recorded, so set_complete is null. Pending members: none.

Reference: fidelity to the chosen source only. Cerbero could not check that /data/studio/backups/aurora-2026-10-01/layout.indd is the version you expect, because there is no earlier reference.
Verification done for this entry: source path and size checked (D5); source digest observed twice, at planning and just before the copy, both equal; destination absent before the copy (D5); NAS-returned destination path equal to the planned one; destination digest equal to the source digest. Format check: not available for .indd files (no registered expert opens them). Equal digests show equal bytes. They do not show that malware is absent.
Failed: none. Out of scope: none. Changed files outside the target: none (none were examined).
Recovery folder: /data/studio/recovered/cerbero-recovery-CAS-0001 (created by Cerbero, approval APV-2). The source was only read. Nothing was moved, overwritten or deleted.
NAS approvals you answered: APV-1 (plan save), APV-2 (folder), APV-3 (copy), APV-4 (receipt save), APV-5 (index save), all granted.
Saved: plan at /data/studio/cerbero-memory/CERBERO-B-0001-01.md (6405 bytes, verified), receipt at /data/studio/cerbero-memory/CERBERO-B-0001-02.md (5631 bytes, verified), index at /data/studio/cerbero-memory/CERBERO-IDX-0001-01.md (604 bytes, verified).

## Limits and next steps
- The recovered file is not a new backup copy. It is on the same NAS as its source and as Cerbero memory, and the failure domains (volume, storage pool, device, site) of these folders are unknown.
- Case CAS-0001 stays open until you confirm the outcome.
- If you want later reviews to check Aurora against approved versions, name the Aurora project folder and ask for a Baseline ("Record the current state of project Aurora"). You can also tell Cerbero which files form an approved set and where the copies are.

## Coverage
Assets checked by digest: 0 of 0 critical (no baseline); ordinary checked by metadata: 0. Target member checked: layout.indd, 1 of 1.
Listings: 1 complete (memory folder, 0 entries), 0 truncated, 0 folders unreadable. The source location /data/studio/backups/aurora-2026-10-01 was not listed.
Digests computed: 6 files, 67593 bytes (source 2, destination 1, plan file 2, receipt file 1). Memory files hashed at load: 0.
Not reviewed: the Aurora project folder (not named), the other files in /data/studio/backups/aurora-2026-10-01, the rest of /data/studio/recovered.
Out of scope: none.
Memory needing review: none.
Not persisted: none.
