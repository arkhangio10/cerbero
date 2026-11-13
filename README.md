# Cerbero: data-resilience Skill for UGREEN AI NAS

Cerbero (`cerbero-guardian`) helps a small studio answer three questions about its project folders on a UGREEN NAS:

- **Guardian:** if this folder or volume fails, can I rebuild the approved delivery?
- **Investigator:** what changed, according to the evidence?
- **Rescuer:** how do I recover the right versions, with proof?

On explicit request it rebuilds a whole approved delivery in a new folder, with a manifest. It then tests what it learned against counterexamples before applying it, and a later session applies a lesson only from its saved, verified records.

It is an orchestration Skill. `SKILL.md` and nine Markdown references delegate all NAS work to UGOS registered experts (`file-agent`, `document-agent`, `knowledge-agent`). It contains no scripts.

Separately, `dev/protected_files/` holds a local development prototype for protected exports: encrypted `.cerbero` copies, controlled access, alerts and revocation. It is not part of the Skill or its ZIP; the Skill does not call it. See [Protected files prototype](#protected-files-prototype-separate-from-the-skill).

> Status (12 November 2026): version 1.2.1 closes the open points of the 1.2.0 closure review: inputs depend on the mode, a save counts only with the exact byte count, records saved again keep their IDs, conflicting duplicate records are not used, claim kinds are fixed, and every report starts with one plain result line. It keeps the fixes of 1.2.0, which corrected the seven defects of the first independent review ([CERBERO_REVIEW_2026-11-10.md](CERBERO_REVIEW_2026-11-10.md)) and the four of the second ([CERBERO_REVIEW_2026-11-12.md](CERBERO_REVIEW_2026-11-12.md)): `python dev/review/reproduce_review.py` passes 7/7 and `python dev/review/reproduce_review_2026_11_12.py` passes 4/4, both unchanged. The package passes the official static checker with zero diagnostics. The decision rules are exercised by a local lab against simulated experts, with memory reloaded only from saved files, including a demo that runs every session in its own process. Model agents followed the real `SKILL.md` against simulated experts ([agent evaluation](submission/AGENT_EVALUATION.md)). Nothing has run on a UGREEN NAS yet. See [what still needs device validation](submission/NAS_VALIDATION_CHECKLIST.md). None of this makes Cerbero production-ready.

## Repository layout

| Path | Content |
|---|---|
| [skill/cerbero-guardian/](skill/cerbero-guardian/) | The Skill: [SKILL.md](skill/cerbero-guardian/SKILL.md) plus [references/](skill/cerbero-guardian/references/). This is the only content of the ZIP. |
| `dist/cerbero-guardian-1.2.1.zip` | Current Skill package: 10 Markdown files, identical to `skill/cerbero-guardian/` (a test checks it). `dist/cerbero-guardian-1.2.0.zip` and `1.0.0.zip` are kept unchanged; 1.1.0 was a draft that was never packaged |
| [submission/](submission/) | [Proposal](submission/PROPOSAL.md) and its [PDF](submission/cerbero-guardian-proposal.pdf), [demo script](submission/DEMO_SCRIPT.md), [declaration](submission/DECLARATION.md), [evaluation report](submission/EVALUATION_REPORT.md), [agent evaluation](submission/AGENT_EVALUATION.md), [NAS validation checklist](submission/NAS_VALIDATION_CHECKLIST.md) |
| [dev/](dev/) | Development lab, never shipped: simulator, reference procedures, evaluator, trace grader, multi-process demo (`dev/tools/run_demo.py`), agent harness (`dev/agent_eval/`), review reproducers (`dev/review/`), fixtures, tests, tools |
| [dev/protected_files/](dev/protected_files/) | Separate local prototype, never shipped: encrypted export, controlled access, alerts and revocation (FastAPI, SQLite, AES-256-GCM), with its own pinned virtual environment, tests and demo. Documented in Spanish in its [README](dev/protected_files/README.md) |
| [CERBERO_BLUEPRINT.md](CERBERO_BLUEPRINT.md), [CERBERO_TECHNICAL_DESIGN.md](CERBERO_TECHNICAL_DESIGN.md) | Product and technical design (Spanish), updated to the implementation |

## Install the Skill

1. Build the package, or use the one in `dist/`. From `dev/`, run:
   - `python tools/fetch_kit.py`: downloads the official kit 0.7.3 and verifies its SHA-256.
   - `python tools/check_skill.py`: runs the official checker.
   - `python tools/build_skill_zip.py 1.2.2`: builds a new version. Existing versions are never overwritten; 1.2.1 is already built.
2. Upload the ZIP to SkillHub, or place the `cerbero-guardian` folder in the assistant skills directory, as the Starter Kit describes. Whether SkillHub expects the top-level folder inside the ZIP must be confirmed on the device.
3. On the NAS, prepare a project folder, the backup or archive folders, and an empty memory folder Cerbero may write to.

## Use

Say, in the UGOS assistant:

- "Record the current state of project Aurora. Delivery 2 is approved: brief.pdf, layout.indd, copy.docx, cover.tif, logo.ai."
- "If the Aurora folder became unavailable, or Volume 1 failed, could I rebuild Delivery 2?"
- "I lost files from Aurora. Find what happened, recover the correct versions that are available and improve the next review."
- "Rebuild Delivery 2 in a new folder." Every file of the delivery, intact ones included, with where it came from and what was checked.
- "Retire policy v2."

Cerbero asks you to confirm three kinds of things:

- the approved set before recovering;
- each recovery plan, by its ID and digest;
- each policy before it becomes active.

Cerbero asks you to confirm each recovery plan by its ID and digest, and the same answer reconfirms the approved set it shows. The NAS may ask for its own approval of every folder it creates, every copy and every save; records are grouped into saves of at most 16 KB, so a recovery usually saves three or four files (case records, plan, receipt, index). If the plan cannot be saved, nothing is created or copied. Recovered files always go into a new folder. Nothing is moved, overwritten or deleted. The receipt says separately how many copies were verified and whether the delivery you asked for is complete; anything it could not check stays listed by name.

## Demo

`python dev/tools/make_demo_dataset.py` writes the synthetic Aurora dataset (scenario S00V) to `dev/out/demo-dataset/`, with:

- the `nas/` tree to upload, where brief.pdf, copy.docx and cover.tif are valid files that open after recovery and the rest are binary fixtures with project-like names;
- the staging files for the incident;
- the development test cases (`memory-seed/`) and, separately, the holdout test cases (`memory-seed-holdout/`) to add only after the rule is frozen;
- `MANIFEST.md`, with every SHA-256, the kind of each file and the expected outcome.

The timeline is in [submission/DEMO_SCRIPT.md](submission/DEMO_SCRIPT.md). It is a plan for a recording that has not been made.

The same story runs in the lab with `python dev/tools/run_demo.py all`: baseline, incident, recover, rebuild, learn, a review in a new session, retire, and the review again. Each session is a separate Python process on a simulated NAS kept on disk (`dev/out/demo-run/nas/`); only the files of the memory folder pass from one session to the next. The recovered and rebuilt PDF, DOCX and TIFF files can be opened there, and `dev/out/demo-run/reports/` holds what each session reported, including the new session that names the policy it loaded, its frozen digest, its evaluation and the approval.

## Development lab

From `dev/`:

| Command | What it does |
|---|---|
| `python -m unittest discover -s tests` | 151 tests: simulator, reversible record format, eligibility and domain graphs, path scope (memory included), mandatory plan, target and pending members, full rebuild, every required case, safety invariants, persistence across sessions, limits (more than 200 memory files, chained index parts, truncated reads, partial saves, fragments, restarts, collisions, budgets), evaluation order invariance, policy lifecycle and cross-session learning in separate processes, trace grader, agent harness and plan binding, demo formats, official checker, Skill and lab contracts, package shape, submission limits |
| `python review/reproduce_review.py` and `python review/reproduce_review_2026_11_12.py` (or from the repository root with `dev/review/...`) | The reproductions of the two independent reviews: 7/7 and 4/4 pass in 1.2.1 |
| `python tools/run_demo.py all` | The multi-process demo described above |
| `python tools/run_evaluation.py` | Compares A (simple, no memory), B (memory + hashes) and C (full) on isolated state. Writes `submission/EVALUATION_REPORT.md` and `dev/out/evaluation.json`. |
| `python -m cerbero_lab.grader <exported-memory-folder> <scenario.json> [--files <recovery-folder-copy>]` | Grades a memory folder exported from a NAS run: integrity, what the records claim and, with `--files`, the bytes of the recovered files |
| `python agent_eval/runner.py prepare CASE OUT` (also `grade`, `summarize`, `report`) | Agent harness: a model follows the real `SKILL.md` against simulated experts and a scripted user; the grader binds every change to the exact approved plan |
| `python tools/proposal_pdf.py` | Counts the ten answers (at most 500 words), renders and verifies the PDF (at most 1 MB) |

### Test cases

| Requirement | Fixture |
|---|---|
| Legitimate rename with intact content | `S01` |
| Alteration keeping size and date | `S02` |
| Recent wrong copy versus older correct copy | `S03` |
| Incompatible versions of a set | `S04` |
| Copies sharing a failure domain | `S05` |
| Permission denied or incomplete inventory | `S06` |
| Source modified during recovery | `S07` |
| Retry after partial failure | `S08` |
| Document with malicious instructions | `S09` |
| Overbroad policy refuted by a counterexample | policy cases `P1` to `P5` with `fixtures/policies.json`; persisted lifecycle in `run_demo.py` |
| Full rebuild with manifest and format checks | `S00V` (demo, valid PDF, DOCX and TIFF) |
| No recoverable copy | `S11` |
| Approval declined, no prior reference, stale memory, unknown domain | `S12`, `S13`, `S14`, `S15` |
| Main demo incident | `S00` |

### Results (simulation only)

- Over 15 scenarios, each run on its own state with memory loaded only from saved bundles, the full rules (C) recovered 14 of 14 required files with the right version. They made no wrong-version claim, no unwarranted "recoverable" verdict and no state change without approval, and reported the requested target as complete or incomplete correctly in 12 of 12 recoveries.
- The implemented name-and-date flow (A) claimed 6 recoveries with the wrong version.
- Memory with hashes (B) was accurate when its memory was fresh. It was wrong in S05, S06, S14 and S15: shared or unknown failure domains, a stale copy record and truncated listings.
- C costs more expert calls than B (608 against 454) and more approvals (80 against 31, 53 of them memory saves). It hashes fewer bytes.
- C misses one alteration in an ordinary file that keeps size and date (S02), so it cannot report it either; this is a documented trade-off that the learned policy addresses for raw/.
- Since 1.2.0 the receipt overall is the result of the copies, and completeness of the requested delivery is a separate field; the expectations of S00, S02 and S04 changed with that definition (see the report).
- These comparisons are against the baselines implemented in this lab, not against other assistants.

Agent runs ([submission/AGENT_EVALUATION.md](submission/AGENT_EVALUATION.md)), Claude Opus 5.5 subagents following the real `SKILL.md` against simulated experts and a scripted user, one run per case:

- With the packaged 1.2.1 Skill, AG04 to AG13 passed every check of the evaluator, which binds each change to the exact approved plan:
  - a declined plan (AG04);
  - a copy of chosen files without prior reference, which no longer asks for a project folder (AG05);
  - a backup without real path (AG06);
  - Learn with a blind holdout (AG07): the agent's first rule failed a holdout case and was rejected, as in 1.2.0;
  - a full rebuild with manifest (AG08);
  - a new session that applied a learned policy only after checking its saved chain (AG09).
- A learning cycle ran entirely by agents, each session starting from the memory the previous agent run left:
  - AG10 revised the rejected rule, passed new holdout cases it had never seen and activated it with user approval;
  - AG11 applied it in a new session;
  - AG12 retired it;
  - AG13 no longer applied it.
- The 1.2.0 runs are kept in the report for comparison. The AG01 to AG03 traces of the 1.1.0 draft were regraded with the newer evaluator without being rerun (24/24, 11/11, 23/23).
- The runs exposed harness artifacts, documented in the report. One run per case is a smoke test of adherence, not a rate.

The full numbers and caveats are in [submission/EVALUATION_REPORT.md](submission/EVALUATION_REPORT.md). These are results of deterministic reference procedures against simulated experts. They are not evidence of behaviour on UGOS.

## Protected files prototype (separate from the Skill)

`dev/protected_files/` is a small local service added on 12 November 2026:

- **Export:** the owner exports a chosen file to an encrypted `.cerbero` container. The original is never modified.
- **Open:** a recipient opens the container only through the service's web viewer. The service checks the account, the permission, the integrity (registered SHA-256 and AES-GCM tag) and the document state before decrypting on the server.
- **Lost or revoked:** marking a document lost or revoked denies every new content request once the change is committed. That includes earlier sessions and copies of the same container, and survives a restart.
- **Alerts:** denied attempts create persistent events, panel notifications and, optionally, an email through a local SMTP test mailbox. Authorized opens are audited too.

It listens on loopback only and uses synthetic data. It is not integrated with UGOS: the Skill does not consume it, no UGOS command calls it, and its per-document audit export is for manual review.

From `dev/protected_files` in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m cerbero_pf demo --fresh
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On 12 November 2026:

- the demo passed its 15 checks;
- the prototype suite ran 75 tests: 74 passed and 1 was skipped, a file-symlink case that needs privileges on this Windows; a directory junction covers path containment instead. The 75 include regressions for the 10 medium- and low-severity findings of an adversarial review (concurrent bypass of the login and open limits, unbounded JSON bodies before authentication, and others), which are fixed or mitigated; the review found no path that releases content improperly;
- the Skill suite passes 151/151, the review reproducers 7/7 and 4/4, and the official checker reports 0 errors and 0 warnings.

Limits:

- it cannot track a file outside the viewer or detect offline decryption;
- IP location is approximate and the browser location is client-declared, so neither proves identity;
- revoking does not erase content already delivered;
- losing the service, its database or its master key can make these exports unrecoverable;
- it does not protect against a fully compromised server.

Install, configuration, threat model, container format and key custody are in [dev/protected_files/README.md](dev/protected_files/README.md).

## Limits

- Cerbero acts only when invoked. It has no background monitoring, attack blocking, network isolation, snapshot or backup management, or web browsing; the catalog exposes none of these.
- Recycle-bin `restore` is not used until its path resolution and effect are validated.
- Digests and memory live on the same NAS, so they are not an independent root of trust if the NAS itself is compromised.
- Recovery needs an existing copy. Cerbero cannot decrypt without keys or repair disks.
- Each memory save may need a confirmation on the device (approval fatigue). This must be measured on the NAS.
- The 16 KB save budget, the 200-entry listings and the session budgets are design defaults of the Skill and the lab, not measured UGOS limits.
- Checking a real path and then reading it are two operations; Cerbero detects a link changed between them only through the real path the later operation reports, and claims no atomicity.
- Where the UGOS model and experts process data is not documented in the catalog; the Skill adds no external service, but fully local processing is not claimed until it is checked on the device.
- The rules text was read from a public verbatim copy because the Devpost page returned HTTP 403 to automated access. Confirm the requirements on the official page before submitting.
