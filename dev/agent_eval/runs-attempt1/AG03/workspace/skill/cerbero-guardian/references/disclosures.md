# Disclosures

## Developed for the UGREEN Hackathon 2026

All files of this Skill (`SKILL.md` and every file under `references/`) were written during the Hackathon period for this submission: the orchestration workflow, memory record format, recoverability rules, investigation selection order, recovery protocol and policy lifecycle. No previously developed Skill or material was reused.

## Runtime components

- This package contains Markdown only: no scripts, binaries, manifests, credentials or personal data.
- At run time it delegates to experts registered on UGOS: `file-agent` (`ug-filesystem`, `file-workflow`), `document-agent` (`ug-document`) and `knowledge-agent` (`ug-knowledge`). These are provided by the UGREEN platform.
- No third-party component, library, external service or download is used at run time.

## Data flows

- File contents, paths and digests stay on the NAS and in the memory folder the user authorizes.
- `answer-official` receives a general question written by Cerbero, without NAS file names, paths or contents. The catalog does not say whether that capability is served on the device or by a UGREEN service; its handling is governed by UGREEN.
- Cerbero sends no file content, path or digest to any service, and calls no service outside the registered experts.

## Development-time tools (not part of this package)

| Tool | Source | License | Use |
|---|---|---|---|
| Uliya Skill Kit 0.7.3 | UGREEN Hackathon Starter Kit | UGREEN developer tools agreement | capability catalog, Skill standard and the official static checker |
| Node.js 22 | nodejs.org | MIT | running the official checker |
| Python 3.11 standard library | python.org | PSF License 2.0 | synthetic fixtures, deterministic evaluator, tests, packaging |
| PyMuPDF | pymupdf.io | AGPL-3.0 | rendering the proposal PDF locally |
| pypdf | pypi.org/project/pypdf | BSD-3-Clause | checking the proposal PDF text and word count |

## AI tools

- Claude Code (Anthropic), model Claude Opus 5.5: used under the direction and review of the entrant to read the kit and rules, draft and revise this Skill, write the development evaluator, fixtures and tests, and draft the proposal, README, demo script and these disclosures.
- On the NAS, the Skill is executed by the UGOS assistant and its registered experts; no other AI model is required.

## Test data

All fixtures and the demo dataset are synthetic bytes generated for this project. No personal files, real malware or third-party media are included or required.
