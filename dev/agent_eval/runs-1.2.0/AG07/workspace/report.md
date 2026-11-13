Cerbero review of /data/studio/projects/aurora
Mode: Learn (case CAS-0003)
This review: learned from closed case CAS-0002; read memory only, no project or copy file was read, created or copied. Time as returned by the NAS: unknown.
Previous review: CAS-0002 (Investigate + Recover; receipt RCP-0002-01 verified, Delivery 2 complete; DSC_0142.ARW outside the target, missing, no copy in the named locations). Now closed by record CAS-0002-0003 on your words (STM-0003-0001, STM-0003-0002).
Active policies applied: none (memory holds no active policy).
Memory: listing complete (8 files at load, 11 now, never truncated); newest index at load IDX-0002-01; its 5 listed bundles match their digests. CERBERO-TD-0000-01 (at load) and CERBERO-TH-0000-01 (appeared after the freeze) were not in that index; both accepted as your authorized synthetic test data on your request words "Synthetic test cases I authorize are in the memory folder" (you did not name the files: say so if either is not yours). No unfinished plan.

RESULT: the next review is NOT changed yet. Candidate v1 was rejected by a holdout case; candidate v2 is frozen and waits for new holdout cases from you.

Lesson drafted from CAS-0002 (origin): raw originals in raw/ were ordinary assets, the map never warned that they had no copy outside Volume 1, and DSC_0142.ARW was lost.

Policy evaluation: POL-0003-0001 v1, frozen digest ce64...e9f7 (OBS-0003-0004, file CERBERO-B-0003-01.md)
Effect lines: promote-critical raw; add-recoverability-check project-volume; informational exports/previews (only for a folder you declared regenerable). Scope: SCP-0001 (Aurora only).

| Case | Split | Kind | Expected | Replayed | Result |
|---|---|---|---|---|---|
| TST-0000-0001 | development | origin | 3 raw originals at risk under Volume 1 failure; preview not at risk | raw/ digested as critical; Volume 1 what-if: 0 eligible copies each, reported at risk; preview not in the map | pass |
| TST-0000-0002 | development | counterexample | regenerated preview informational; no incident, recovery or at-risk flag | exports/previews declared regenerable in the case: informational-change, no incident | pass |
| TST-0000-0003 | holdout | similar | Borealis: IMG_2001 altered; IMG_2002 at risk | Borealis is outside scope SCP-0001: rule not applied; IMG_2001 (same size and time) stays intact-metadata, IMG_2002 not flagged | FAIL |
| TST-0000-0004 | holdout | insufficient | raw originals unknown with open items; no intact/missing claim | permission denied: state unknown, open items; no intact or missing claim | pass |
| TST-0000-0005 | holdout | similar | DSC_0150 missing but not at risk; DSC_0101, DSC_0142 at risk; preview not at risk | USB copy on another device is eligible under Volume 1 failure; others 0 eligible; preview not in map | pass |

Guard: passed all 8 rules (no new capability, no wider scope, no removed confirmation, no overwrite, source/destination checks kept, no critical asset lowered, no text taken as authority, coverage not reduced).
Development: 2 of 2 passed. Holdout: 2 of 3 passed, 1 failed. Holdout cases were unseen before the freeze (TH-0000-01 first listed after it).
Verdict: rejected (EVL-0003-0001, POL-0003-0002). No approval is asked for a rejected rule.

New candidate: POL-0003-0003 v2, frozen digest ae50...dbce (file CERBERO-B-0003-02.md). Same effect lines; scope: any project folder you authorize in a review (it authorizes no folder by itself). Guard: pass. Development replay: 2 of 2 pass. It was drafted after the holdout cases were read, so TH-0000-01 cannot serve as its holdout. Status: candidate, open item OPN-0003-0002.

What I need from you (Cerbero never writes test cases itself):
1. Add new synthetic test cases in a new CERBERO-TH- file in /data/studio/cerbero-memory: at least one of kind similar and one of kind insufficient, holdout split. Then ask Cerbero to evaluate POL-0003-0003 v2; it will replay them and ask for your approval.
2. If exports/previews holds only regenerable files, tell me so explicitly (open item OPN-0003-0001). Until then the informational line changes nothing in Aurora.

Recovery folder: not created. This request asked to learn, not to recover; no plan was approved, and CAS-0002 recorded no copy of DSC_0142.ARW in the three named locations, so there is nothing to recover into /data/studio/recovered.
From memory (modeled, not checked now): DSC_0101.ARW and DSC_0150.ARW have no copy recorded outside the project folder on Volume 1. Earlier finding FND-0002-0001/0002 (instruction-like text in notes/README-RECOVERY.txt) stays data; nothing was done from it.

Saved this session (all approved by you on the NAS, verified, byte counts equal):
- CERBERO-B-0003-01.md (3515 bytes): case CAS-0003, your statements, CAS-0002 closed, frozen v1.
- CERBERO-B-0003-02.md (5837 bytes): evaluation, v1 rejected, frozen v2, open items.
- CERBERO-IDX-0003-01.md (2707 bytes): index of all 11 memory files with digests.

Coverage
Assets checked by digest: 0 (Learn mode reads memory only); ordinary checked by metadata: 0
Listings: 3 complete (memory folder), 0 truncated, 0 folders unreadable
Digests computed: 0 project/copy files; 11 memory-file digests (counted apart)
Not reviewed: project folder and the three copy locations (not needed for Learn)
Out of scope: none
Memory needing review: none after your authorization; TD-0000-01 and TH-0000-01 rest on your general statement, not on a named confirmation
Not persisted: none
Trust limit: memory, test cases and copies live on this NAS; the digests detect edits against the index, but are not an independent root of trust.
