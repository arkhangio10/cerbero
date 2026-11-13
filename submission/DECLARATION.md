# Cerbero: components, sources, licenses and AI tools

Project: Cerbero (Skill `cerbero-guardian`, version 1.2.1), UGREEN Hackathon 2026 on AI NAS, Open Innovation track. Prepared on 10 November 2026 and updated on 12 November 2026.

## Original work developed for the Hackathon

The following were written during the Hackathon period for this project:

- the Skill package: `SKILL.md` and the nine Markdown references;
- the development lab: simulator, evaluator, trace grader, fixtures and tests;
- the agent harness that lets a model follow the real `SKILL.md` against simulated experts;
- the multi-process demo (`dev/tools/run_demo.py`) that runs each session in its own process on a simulated NAS kept on disk;
- the tools for packaging, PDF rendering and demo data, including the valid-format synthetic demo files;
- the design documents and these submission materials;
- a separate local prototype for protected exports (`dev/protected_files/`, added on 12 November 2026). It covers encrypted `.cerbero` copies, a web viewer with controlled access, alerts and revocation, and has its own tests and demo. It is not part of the Skill and is described below.

No previously developed Skill, code or submission material was reused. The entrant owns this work. No open-source license has been applied to it yet.

## Components

| Component | Where used | Source | License | Shipped in the Skill ZIP |
|---|---|---|---|---|
| UGOS registered experts (`file-agent`, `document-agent`, `knowledge-agent`) | Skill run time on the NAS | UGREEN UGOS | UGREEN platform terms | no (platform) |
| Uliya Skill Kit 0.7.3, including its capability catalog 2.0.0, standard and static checker | development only: capability evidence and static checks | `ai.ugreen.com/pages/hackathon-starter-kit` (archive SHA-256 `cf557e5a022e4297892f39768132855154232efdedeb726b2845450ccd70e1b3`) | UGREEN developer tools agreement | no; fetched locally by `dev/tools/fetch_kit.py`, not redistributed |
| Node.js 22 | development only: runs the official checker | nodejs.org | MIT | no |
| Python 3.11 standard library | development only: evaluator, tests, packaging | python.org | PSF License 2.0 | no |
| PyMuPDF | development only: renders the proposal PDF (Helvetica base-14 font, nothing embedded) | pymupdf.io | AGPL-3.0 | no |
| pypdf | development only: checks the text of the proposal PDF and of the demo PDF | pypi.org/project/pypdf | BSD-3-Clause | no |
| Pillow, python-docx | development only: one manual check that the demo TIFF and DOCX open (log in `dev/review/logs/`); not used by the tests | pypi.org | MIT-CMU (HPND), MIT | no |

The Skill ZIP (`dist/cerbero-guardian-1.2.1.zip`; versions 1.2.0 and 1.0.0 are kept unchanged) contains only the ten Markdown files of `skill/cerbero-guardian/`: no scripts, binaries, credentials, personal data or third-party material.

### Protected files prototype (development only, not in the Skill ZIP)

These packages are installed in an isolated virtual environment (`dev/protected_files/.venv`) from the exact versions in `dev/protected_files/requirements.txt`, downloaded from pypi.org. None is redistributed.

| Component | Version | Use | License |
|---|---|---|---|
| FastAPI, Starlette | 0.162.5, 1.10.0 | web API and pages served by the prototype; FastAPI's native telemetry is explicitly disabled | MIT, BSD-3-Clause |
| uvicorn | 0.54.0 | local server, loopback only, `proxy_headers=False` | BSD-3-Clause |
| cryptography | 50.0.2 | AES-256-GCM (AEAD) for containers and key wrapping | Apache-2.0 OR BSD-3-Clause |
| aiosmtpd | 1.4.6 | local SMTP test mailbox | Apache-2.0 |
| httpx | 0.28.1 | test client and demo HTTP client | BSD-3-Clause |
| Pydantic, pydantic-core | 2.14.3, 2.50.4 | request validation (FastAPI dependency) | MIT |
| Other transitive dependencies: anyio, h11, httpcore, click, idna, certifi, cffi, pycparser, attrs, atpublic, annotated-types, annotated-doc, typing-inspection, typing-extensions, opentelemetry-api | pinned in `requirements.txt` | dependencies of the above | MIT, BSD-3-Clause, MPL-2.0 (certifi), MIT-0 (cffi), Apache-2.0 (atpublic, opentelemetry-api), PSF-2.0 (typing-extensions) |
| Playwright for Python, with Chromium | 1.58.0 | optional browser test only | Apache-2.0 (Chromium: BSD-style) |
| SQLite (Python standard library) | bundled with Python 3.11 | persistence | public domain |

## External services and data flows

- At run time, Cerbero delegates only to UGOS registered experts and integrates no service of its own. It writes memory only to the folder the user authorizes.
- Not verified: where the UGOS assistant model and each expert run, and whether prompts, paths, contents or digests leave the device. The catalog does not document it; it has to be checked in the UGOS configuration of the assigned device. This submission does not claim fully local or offline processing.
- `answer-official` receives general questions without any NAS file data. The catalog does not document where that capability runs.
- The development tools make one network request: downloading the official kit from the URL above. Installing the prototype's virtual environment downloads its pinned packages from pypi.org.
- **Protected files prototype.**
  - It listens on loopback only and sends nothing to external services by default.
  - IP geolocation is off unless a local CSV database is configured; the "simulated" provider is labelled SIMULADO.
  - SMTP is off unless configured, and a non-loopback mail server requires an explicit `allow_external = true`.
  - Emails carry no document content, keys, IP addresses or coordinates.
  - Browser location is requested only after an explicit user action and notice.
  - It has not run on a UGREEN NAS. It is not integrated with UGOS, and the Skill does not consume it.

## Data

All fixtures and the demo dataset are synthetic: every byte is generated from text seeds in `dev/fixtures/`, and no content comes from a real project, person or camera. Two kinds of files must be told apart:

- **Valid-format synthetic files.** In the demo dataset (scenario S00V), brief.pdf, copy.docx and cover.tif (and the altered cover) are generated as valid PDF, DOCX and TIFF files that open in standard readers. Their content is synthetic text or a generated pixel pattern.
- **Binary fixtures with project-like names.** The other files (`.indd`, `.ai`, `.ARW`, `.ase`, `.jpg` and the fixtures of the other scenarios) only carry a name and a deterministic byte pattern; they are not valid files of that format.

The protected files prototype also uses only synthetic data:

- the demo document is a fictitious contract;
- the demo accounts get random passwords on each run;
- the test fixtures (including the sample IP-location rows and browser coordinates) are labelled test data and are not presented as real results.

No personal data, real malware or third-party media is used. The "malicious" note in the demo is plain synthetic text used to test that instructions inside files are treated as data.

## Sources consulted

The first three rows were read while the Skill was implemented. The other rows are cited in the project design documents written before the implementation.

| Source | Use |
|---|---|
| Official rules, `ugreenhackathon.devpost.com/rules` | Requirements. Automated access returned HTTP 403, so the rules text was read from a public verbatim copy in a third-party repository (`github.com/bgrubbs1/ugreen-story-reel`, file `research/rules.txt`). Nothing else from that repository was used. The entrant must confirm the requirements on the official page. |
| Hackathon page `ai.ugreen.com/pages/ugreen-hackathon` and Starter Kit page | Dates, tracks, judging criteria, setup |
| Uliya Skill Kit 0.7.3 | Skill format, capability catalog, checker rules |
| UGREEN support: Files Recycle Bin guide (article 159); Snapshot user guide (article 654) | Confirmed that these product features exist but are not exposed to the Skill. Neither is used. |
| NIST SP 800-160 Vol. 2 Rev. 1; CISA/MS-ISAC Ransomware Guide | General resilience concepts: anticipate, withstand, recover, adapt; independent and tested copies. No text reused. |
| "Agentic Context Engineering" (arXiv 2510.04618); Anthropic, "The components of agent memory" | Background on memory that is revised against experience. No results attributed to Cerbero. |

## AI tools

| Tool | Principal uses |
|---|---|
| Codex (OpenAI); model version not recorded | Used under the entrant's direction for research, the product and architecture documents (`CERBERO_BLUEPRINT.md`, `CERBERO_TECHNICAL_DESIGN.md` in their first versions), and the independent review of version 1.0.0 (`CERBERO_REVIEW_2026-11-10.md`, `dev/review/reproduce_review.py`), whose seven defects are fixed. |
| Second independent review, 12 November 2026 (`CERBERO_REVIEW_2026-11-12.md`, `dev/review/reproduce_review_2026_11_12.py`) | Found four further defects (N01 to N04), fixed in version 1.2.0. The tool that produced it is not recorded in the review and is not stated here. |
| Claude Code (Anthropic), model Claude Opus 5.5 | Used under the entrant's direction and review to: read the kit, catalog and rules; draft and revise the Skill and its references; write the simulator, evaluator, grader, fixtures, tests, agent harness and tools; fix the defects reported by the review; update the design documents; draft the proposal, README, demo script and this declaration. A second Claude instance reviewed the 1.0.0 Skill text adversarially, and its findings were applied. On 12 November 2026, the same tool wrote the protected files prototype (`dev/protected_files/`): its code, interface, tests, demo and documentation. A Claude subagent reviewed the prototype's security adversarially. |
| Claude Opus 5.5 subagents | Played the UGOS assistant in the local agent evaluation (`submission/AGENT_EVALUATION.md`): they read the real `SKILL.md` (the 1.1.0 draft for AG01 to AG03, version 1.2.0 and then the packaged 1.2.1 for AG04 to AG09, and 1.2.1 for the learning chain AG10 to AG13) and answered simulated experts. This is not the UGOS model. |
| UGOS assistant and experts on the NAS | Execute the Skill at run time. The package requires no other model. |

No other AI tool was used to produce this submission.
