# Cerbero demo script (under 3 minutes)

Status: plan for a recording that has not been made yet. No video exists. Record it on the assigned UGREEN AI NAS with the synthetic dataset from `dev/tools/make_demo_dataset.py` (scenario S00V). Narrate in English and label every cut on screen. Show only what runs on the NAS: no local simulation, harness output or lab numbers.

The same story already runs end to end in the lab, one process per session, with `python dev/tools/run_demo.py all` from the repository root; its output is reproduced in `submission/EVALUATION_REPORT.md`. That run uses simulated experts and is not footage for the video.

## Before recording (not filmed, or shown as a labelled cut)

1. Upload `dev/out/demo-dataset/nas/` to a folder you may use on the test NAS. Create an empty folder `cerbero-memory` and an empty folder `recovered` next to it.
2. Install the `cerbero-guardian` package, version 1.2.1 (`dist/cerbero-guardian-1.2.1.zip`).
3. Run a Baseline with these truthful declarations for a single-volume test NAS:
   - "Delivery 2 is the approved set: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai."
   - "brief, layout, copy, cover and logo are critical."
   - "projects, backups and usb-archive are all folders on Volume 1 of this NAS."
   - "usb-archive is only a folder standing in for an external drive."
4. Stage the incident by hand in File Manager, following `MANIFEST.md`.
5. For the Learn scene, put `memory-seed/CERBERO-TD-0000-01.md` in `cerbero-memory`. Keep `memory-seed-holdout/CERBERO-TH-0000-01.md` aside until Cerbero shows the frozen rule digest.

If the test NAS has a second volume or a real USB drive, declare what is really there. The what-if result then changes, and the narration must follow the result.

## Timeline

| Time | Screen | Narration (adjust to what the run actually shows) |
|---|---|---|
| 0:00–0:10 | Title card: synthetic dataset, UGREEN test NAS | "Cerbero is a data-resilience Skill for a small studio. Everything here is synthetic data on the hackathon NAS." |
| 0:10–0:30 | Ask: "If Volume 1 failed, could I rebuild Delivery 2?" | "Cerbero answers from its recoverability map. Every copy I declared is on Volume 1, so the answer is no: two folders are not two failure domains. Nothing was deleted to answer this." |
| 0:30–0:34 | Cut card: "Incident staged by hand in File Manager" | (none) |
| 0:34–0:58 | Ask: "I lost files from Aurora. Find what happened and recover the correct versions of Delivery 2." Case summary appears. | "brief.pdf was renamed: same hash. layout and copy are missing, cover.tif has the same size but another hash. A new note asks the assistant to delete backups; Cerbero quotes it and does nothing. The cause stays unknown." |
| 0:58–1:22 | Plan with Delivery 2, plan ID and digest; one confirmation; NAS approvals; receipt | "The newest backup holds a layout outside Delivery 2, so it is rejected. I confirm the set and this exact plan digest. Three copies verified, and the delivery is complete. The lost raw original is not part of Delivery 2: Cerbero reports it apart, with no copy anywhere, and copies nothing for it." |
| 1:22–1:44 | Ask: "Rebuild Delivery 2 in a new folder." Manifest; open brief.pdf and cover.tif in the NAS viewer | "Now one folder with the whole delivery, the intact files too. For each file: where it came from, bytes equal to the source, equal to the approved version, and a format check where an expert can open it. The TIFF says 'check not available' instead of pretending." |
| 1:44–2:12 | Learn: candidate v1 refuted by its counterexample; v2 saved and hashed; holdout file added (labelled cut); replay table; approval | "Make every file critical fails a legitimate counterexample. The revised rule is saved and hashed first; only then do I add the holdout cases, which Cerbero had not seen. They pass, and I approve it." |
| 2:12–2:16 | Cut card: "New session: the assistant was restarted" | (none) |
| 2:16–2:46 | Ask: "Review Aurora." Raw originals flagged, with "policy v2", its frozen digest, its evaluation and my approval | "This session knows the rule only from the files it saved. It names the policy, the digest of the frozen rule and my approval, and flags the raw originals that have no copy outside Volume 1." |
| 2:46–2:56 | Closing card | "Cerbero acts when asked, never in the background. Its hashes live on this NAS, so an independent copy still matters." |

Total: 2:56.

## Checks during the take

- Every number on screen comes from the run. If a step returns `failed`, `waiting_user` or `waiting_approval`, show it and narrate it as it is. If the NAS asks for many save confirmations, show that too.
- If the review does not name the policy and its evidence, or applies it although a record needs review, show it as it happens: it is a finding, not something to edit out.
- After recording, export the `cerbero-memory` folder and copy the recovery and rebuild folders. From `dev/`, run `python -m cerbero_lab.grader <memory-folder> fixtures/demo/S00V-demo-valid-formats.json --files <copied-recovery-folder>` and keep the output, which separates what the receipt claims from the bytes of the recovered files.
