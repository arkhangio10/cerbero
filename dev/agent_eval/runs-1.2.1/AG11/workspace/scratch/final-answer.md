If Volume 1 failed, you could lose 5 recorded files that have no copy outside that volume: raw/DSC_0101.ARW, raw/DSC_0150.ARW, fonts-license.pdf, palette.ase and exports/previews/cover-preview.jpg. Two unrecorded items have no known copy either. Delivery 1 and Delivery 2 could still be rebuilt from the copies on Volume 2 and on the USB archive. This answer is predicted from Cerbero memory: the copies were not re-checked today.

```text
Cerbero review of /data/studio/projects/aurora
Mode: What-if (scenario: failure of Volume 1, the volume you declared for the project folder, DOM-0001-0001)
This review: case CAS-0005. Covered both approved sets and every recorded file of the project. The project folder was listed now (complete to depth 8) and its 2 raw files were hashed now. Copies are modeled from memory. Time: unknown (the NAS returned none).
Previous review: CAS-0004 (Learn, policy v2 activated). The last check of the project files was CAS-0002 (Investigate and Recover, closed; receipt RCP-0002-01 verified, Delivery 2 complete).
Active policies applied: POL-0004-0003 version 2, loaded from CERBERO-B-0004-02.md; frozen rule digest cb23...7032 (POL-0004-0001 in CERBERO-B-0004-01.md, equal to the digest the NAS returned now); evaluation EVL-0004-0001 (development origin and counterexample, holdout similar and insufficient, all pass); approved by you (STM-0004-0003: "Yes. I approve POL-0004-0001."); invariant guard passed.
Memory: 16 files listed, listing complete; newest index IDX-0004-01; 11 files hashed, all equal to the index; 0 need review; 4 not read because this request did not need them (IDX-0001-01, IDX-0002-01, IDX-0003-01 superseded; TH-0000-01, holdout of the rejected policy v1).
```

How the policy changed this review: raw/DSC_0101.ARW and raw/DSC_0150.ARW were hashed and included in the map as critical files because of policy POL-0004-0003 v2 (frozen digest cb23...7032, evaluation EVL-0004-0001 with holdout cases, approved by you). Without it they would only have been modeled from memory. Its other line, "informational exports/previews", was not applied, because you have never declared that folder regenerable. So cover-preview.jpg is reviewed like any other file.

## Files you could lose (Volume 1 failure)

| Required version | Eligible copies | Uncertain copies | Evidence level | Why |
|---|---|---|---|---|
| raw/DSC_0101.ARW VER-0001-0009 (2cca...5442) | 0 | 0 | none | only copy is the project file on Volume 1; digest verified now, intact (OBS-0005-0004) |
| raw/DSC_0150.ARW VER-0001-0011 (88e9...6004) | 0 | 0 | none | only copy is the project file on Volume 1; digest verified now, intact (OBS-0005-0004) |
| fonts-license.pdf VER-0001-0005 (c0a5...3be8) | 0 | 0 | none | only copy is in the project (CPY-0001-0005); size and time unchanged, not hashed |
| palette.ase VER-0001-0008 (2036...e6f6) | 0 | 0 | none | only copy is in the project (CPY-0001-0008); size and time unchanged, not hashed |
| exports/previews/cover-preview.jpg VER-0001-0004 (ecc1...03f0) | 0 | 0 | none | only copy is in the project (CPY-0001-0004); not declared regenerable |

Verdict for these versions: `not-recoverable` with the sources available (MAP-0005-0003). Cerbero inferred this because the recorded inventories of your three copy folders are complete. Those inventories date from the first Baseline (CAS-0001).

Already lost before this review: raw/DSC_0142.ARW (VER-0001-0010). It has been missing since CAS-0002 and has no copy in the named locations. It is still absent today.

Not evaluable, because no version of them is recorded and no copy is known:
- notes/README-RECOVERY.txt (237 bytes). It contains instruction-like text, already recorded as findings FND-0002-0001 and FND-0002-0002. Cerbero took no action from it.
- The current content of cover.tif (digest 93bf...7275, OBS-0002-0004). It differs from the approved version since CAS-0002. The approved cover.tif can be rebuilt, but the altered bytes now in the project would be lost.

## Delivery 2 (SET-0001-0002, your statement STM-0001-0005)

| Required version | Eligible copies | Uncertain copies | Evidence level | Why |
|---|---|---|---|---|
| brief.pdf VER-0001-0001 (9d2c...9055) | 1 | 0 | modeled | CPY-0001-0012 in backups/aurora-2026-10-01 (Volume 2) |
| layout.indd VER-0001-0006 (84a4...1e1b) | 1 | 0 | modeled | CPY-0001-0015 in backups/aurora-2026-10-01 (Volume 2) |
| copy.docx VER-0001-0002 (0745...03c4) | 2 | 0 | modeled | CPY-0001-0013 and CPY-0001-0017, both on Volume 2 |
| cover.tif VER-0001-0003 (2c36...40ef) | 2 | 0 | modeled | CPY-0001-0014 and CPY-0001-0018, both on Volume 2 |
| logo.ai VER-0001-0007 (1dbd...0eda) | 2 | 0 | modeled | CPY-0001-0016 (Volume 2) and CPY-0001-0023 (USB archive) |

Verdict: `recoverable`, evidence level modeled (MAP-0005-0001). Weak point: brief.pdf and layout.indd each have a single copy, in backups/aurora-2026-10-01.

## Delivery 1 (SET-0001-0001, your statement STM-0001-0004)

| Required version | Eligible copies | Uncertain copies | Evidence level | Why |
|---|---|---|---|---|
| brief.pdf VER-0001-0012 (5a52...5f37) | 1 | 0 | modeled | CPY-0001-0019 in usb-archive/aurora |
| layout.indd VER-0001-0013 (708f...e71d) | 1 | 0 | modeled | CPY-0001-0022 in usb-archive/aurora |
| copy.docx VER-0001-0014 (83d7...4dfa) | 1 | 0 | modeled | CPY-0001-0020 in usb-archive/aurora |
| cover.tif VER-0001-0015 (2f54...d8c6) | 1 | 0 | modeled | CPY-0001-0021 in usb-archive/aurora |
| logo.ai VER-0001-0007 (1dbd...0eda) | 2 | 0 | modeled | CPY-0001-0016 (Volume 2) and CPY-0001-0023 (USB archive) |

Verdict: `recoverable`, evidence level modeled (MAP-0005-0002). Four of its five files depend only on the USB archive.

## Evidence

- Predicted by the model: Delivery 2 recoverable, Delivery 1 recoverable, and the 5 files above would be lost.
- Copies verified now: none outside Volume 1, because no copy folder was re-checked in this review. The 2 raw files were verified now, but they are in the project, which the scenario excludes.
- Recovery rehearsed before (historical): receipt RCP-0002-01 (plan PLN-0002-01, approved by its digest 314b...c754) copied the Delivery 2 files copy.docx, cover.tif and layout.indd from backups/aurora-2026-10-01 (CPY-0001-0013, CPY-0001-0014, CPY-0001-0015), with verified digests. This shows those copies worked then. It does not show they are still there or still correct.

## What blocks a firmer answer

- You have not stated a storage pool or site for any location, and the volume of the USB archive is unknown (STM-0001-0003). Volume 1 and Volume 2 are on the same NAS. If they share a storage pool, a pool or device failure could take both, and that scenario was not evaluated (OPN-0005-0001).
- The USB archive is counted as outside the failure only by inference: you declared it an external drive, a different device from this NAS (CLM-0005-0011). Its path, /data/studio/usb-archive/aurora, is in the same folder tree as the project. That proves nothing either way.
- Every copy outside the project was last observed in the first Baseline (CAS-0001, time unknown). Copies added to or removed from those folders since then are not known (OPN-0005-0002).

## Contradictions found in memory

The project copy records of brief.pdf (CPY-0001-0001), copy.docx (CPY-0001-0002), layout.indd (CPY-0001-0006) and raw/DSC_0142.ARW (CPY-0001-0010) point to paths the project no longer holds. The record of cover.tif (CPY-0001-0003) no longer matches the content observed in CAS-0002. Cerbero recorded the contradictions (CLM-0005-0006 to CLM-0005-0010) and marked these records `needs-review` (CPY-0005-0001 to CPY-0005-0005). No verdict changes, because these copies are on Volume 1 and the scenario excludes them anyway.

Current project state, from the listing of this review: copy.docx and layout.indd are not in the project. brief.pdf is not at its recorded path; CAS-0002 found its approved content in brief-FINAL.pdf. The files recovered in CAS-0002 under /data/studio/recovered were not checked, because that folder was not named in this request. Recovered files do not count as backup copies.

Note on the active policy: CERBERO-TH-0000-02.md, which holds its holdout cases, has a modification time (10000) lower than the frozen candidate file (10001). Modification times do not show when a file was created. CAS-0004 recorded that file as absent from the listing taken before the freeze (OBS-0004-0002). The activation checks passed. The policy evidence also has recorded limits: holdout cases from one project only, and no holdout counterexample (OPN-0004-0002).

## What you can do

- To protect the 5 files at risk, copy them to a location on another volume or device. Cerbero does not create or manage backups. Then ask for a Baseline so that Cerbero records the new copies and their domains.
- Ask "verify the copies now" if you want the copies outside Volume 1 re-checked by digest. These checks are read-only and would raise the evidence from modeled to verified-now.
- Tell Cerbero the storage pool and site of each location, and the volume of the USB archive, if you know them.

## Coverage

```text
Assets checked by digest: 0 of 5 critical (not needed for this scenario; their state comes from CAS-0002); 2 raw files promoted by policy v2, both intact; ordinary checked by metadata: 3 (cover-preview.jpg, fonts-license.pdf, palette.ase)
Listings: 2 complete (memory folder, 16 entries; project folder, 9 entries to depth 8), 0 truncated, 0 folders unreadable
Digests computed: 2 project files, 131072 bytes; memory digests counted apart: 13 (11 at load, IDX-0004-01, saved CERBERO-B-0005-01.md); budget left: 298 digests, 58 listings
Not reviewed: the three copy folders (modeled from the Baseline, not listed or hashed now); current content of cover.tif, logo.ai, brief-FINAL.pdf, fonts-license.pdf, palette.ase, cover-preview.jpg and README-RECOVERY.txt (not hashed now); /data/studio/recovered (not named)
Out of scope: none rejected
Memory needing review: none
Not persisted: none. Saved: /data/studio/cerbero-memory/CERBERO-B-0005-01.md (15787 bytes, verified, digest 58b7...3ffc) and /data/studio/cerbero-memory/CERBERO-IDX-0005-01.md (4110 bytes, verified)
```

Nothing in the project or in the copy folders was created, moved, copied or deleted.