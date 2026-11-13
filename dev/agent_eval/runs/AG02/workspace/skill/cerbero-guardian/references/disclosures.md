# Disclosures

## Developed for the UGREEN Hackathon 2026

All files of this Skill (`SKILL.md` and every file under `references/`) were written during the Hackathon period for this submission: the orchestration workflow, memory record format, recoverability rules, investigation selection order, recovery protocol and policy lifecycle. No previously developed Skill or material was reused.

## Runtime components

- This package contains Markdown only: no scripts, binaries, manifests, credentials or personal data.
- At run time it delegates to experts registered on UGOS: `file-agent` (`ug-filesystem`, `file-workflow`), `document-agent` (`ug-document`) and `knowledge-agent` (`ug-knowledge`). These are provided by the UGREEN platform.
- No third-party component, library, external service or download is used at run time.

## Data flows

- This Skill adds no service of its own. It delegates only to the registered experts, writes memory only to the folder the user authorizes, and never asks an expert to send data elsewhere.
- What it cannot establish: where the UGOS assistant model and each expert run, and whether any of them send prompts, paths, file contents or digests off the device. The capability catalog does not document this. It depends on the UGOS configuration of the device and must be checked there before any claim of fully local or offline processing.
- `answer-official` receives a general question written by Cerbero, without NAS file names, paths or contents. The catalog does not say whether that capability is served on the device or by a UGREEN service; its handling is governed by UGREEN.

## Development-time tools (not part of this package)

| Tool | Source | License | Use |
|---|---|---|---|
| Uliya Skill Kit 0.7.3 | UGREEN Hackathon Starter Kit | UGREEN developer tools agreement | capability catalog, Skill standard and the official static checker |
| Node.js 22 | nodejs.org | MIT | running the official checker |
| Python 3.11 standard library | python.org | PSF License 2.0 | synthetic fixtures, valid-format demo files, deterministic evaluator, agent harness, tests, packaging |
| Pillow, python-docx | pypi.org | MIT-CMU (HPND), MIT | one manual check that the demo TIFF and DOCX open; not used by the tests |
| PyMuPDF | pymupdf.io | AGPL-3.0 | rendering the proposal PDF locally |
| pypdf | pypi.org/project/pypdf | BSD-3-Clause | checking the proposal PDF text and word count |

## AI tools

- Codex (OpenAI), under the direction of the entrant: research, the product and architecture design documents, and an independent review of version 1.0.0 that reported defects with reproductions. The model version used by Codex was not recorded and is not stated here.
- Claude Code (Anthropic), model Claude Opus 5.5, under the direction and review of the entrant: reading the kit and rules, drafting and revising this Skill, writing the development lab, fixtures, tests and agent harness, fixing the defects of the review, and drafting the proposal, README, demo script and these disclosures. Claude Opus 5.5 subagents also played the assistant in the local agent evaluation, against simulated experts.
- On the NAS, the Skill is executed by the UGOS assistant and its registered experts; this package requires no other AI model.

## Test data

All fixtures and the demo dataset are synthetic bytes generated for this project. In the demo dataset, three files are valid PDF, DOCX and TIFF documents generated from text seeds; the rest only carry project-like names. No personal files, real malware or third-party media are included or required.
