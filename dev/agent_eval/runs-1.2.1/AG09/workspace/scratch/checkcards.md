CHK-0005-0001
doubt: Are the 12 recorded copies outside Volume 1 (CPY-0001-0012..0023) and the 3 raw/ originals still present at their recorded paths, with real paths inside their authorized roots, and with the recorded size?
decision: which copies may be hashed and counted as verified-now under a Volume 1 failure; raw/ digest review required by policy POL-0004-0003 v2
operation: D5 file-agent, 15 paths
outcomes: present, real path inside its location root, same size: hash next (D7); absent, outside root or different size: copy excluded, contradiction recorded
cost: metadata only, read-only
budget_left: 300 digests, 59 listings, 2 GB

CHK-0005-0002 (and 0003, 0004 for the other two locations)
doubt: Does /data/studio/backups/aurora-2026-10-01 (then backups/aurora-2026-11-05, usb-archive/aurora) hold a copy of a version that has no eligible copy recorded outside Volume 1: raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW (65536 bytes), palette.ase (512), fonts-license.pdf (2048)? Is the inventory still complete?
decision: whether those files are reported as lost under a Volume 1 failure (not-recoverable needs a complete inventory of every named location)
operation: D6 file-agent, of any size, depth 8, limit 200; one listing per location (3 sizes x 3 locations would need 9 size-filtered listings)
outcomes: a file of 65536, 512 or 2048 bytes: candidate, hash next; none: no copy in that location; listing incomplete: split with D13, verdict stays undetermined for the gap
cost: one listing per location, read-only
budget_left: 300 digests, 59 listings before the first, 2 GB

CHK-0005-0005
doubt: Do the 12 recorded copies outside Volume 1 still hold their recorded versions, and do raw/DSC_0101.ARW and raw/DSC_0150.ARW still hold VER-0001-0009 and VER-0001-0011?
decision: copies counted as eligible verified-now under a Volume 1 failure; state of the raw originals reported under policy v2
operation: D7 file-agent, 14 files with expected digests from version records
outcomes: equal: eligible verified-now (copies) or intact (raw); different: copy excluded and contradiction recorded, raw altered
cost: 14 digests, 243168 bytes, read-only
budget_left: 300 digests, 56 listings, 2 GB

CHK-0005-0006
doubt: Which files are in /data/studio/projects/aurora now that the map does not cover (added or renamed since the baseline), and does any of them have a same-size file outside Volume 1?
decision: whether the answer "files you could lose" is complete for the project folder, or must name unrecorded files; a project file whose size matches no file in the three completely listed copy folders has no copy outside Volume 1 (exact exclusion by size)
operation: D6 file-agent, of any size, depth 8, limit 200
outcomes: unrecorded file with no size match outside Volume 1: reported as at risk; with a size match: hash candidate pair next; listing incomplete: split with D13, remainder not reviewed
cost: one listing, read-only
budget_left: 286 digests, 56 listings, about 2 GB

CHK-0005-0007
doubt: Do the project files brief-FINAL.pdf (736 bytes), cover.tif (9396) and logo.ai (8192), whose sizes match files outside Volume 1, hold VER-0001-0001, VER-0001-0003 and VER-0001-0007 now?
decision: whether the current content of these Delivery 2 files in the project has a verified copy outside Volume 1, or would be lost with Volume 1 (cover.tif was recorded altered in CAS-0002 and CAS-0003)
operation: D7 file-agent, 3 files with expected digests from version records
outcomes: equal: current content has the eligible copies counted above; different: that content exists only on Volume 1
cost: 3 digests, 18324 bytes, read-only
budget_left: 286 digests, 55 listings, about 2 GB
