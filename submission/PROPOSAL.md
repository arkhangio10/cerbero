# Cerbero: recover the right version, prove it, learn safely

UGREEN Hackathon 2026 on AI NAS | Track: Open Innovation | Skill: `cerbero-guardian`

## 1. One sentence: What does the Skill do?

Cerbero shows whether an approved delivery can still be rebuilt, investigates missing or altered files with hash evidence, recovers or rebuilds the right versions with a verified receipt, and applies lessons only after testing them.

## 2. Who is the target user and problem?

A small creative studio keeping originals and client deliveries on its NAS, without a recovery specialist. When files vanish or change, nobody knows what changed, which copy holds the approved version, or whether backups cover a delivery. Taking each newest copy mixes versions.

## 3. What is your proposed solution?

Three roles over registered NAS experts. Guardian: a recoverability map of approved sets, SHA-256 versions, real copy paths and declared failure domains. Investigator: read-only checks with stated reasons and explicit coverage. Rescuer: recovers, or fully rebuilds, one approved set under a hash-bound plan and receipt, then proposes a lesson that must survive counterexamples.

## 4. What is the Core User Flow?

"I lost files from Aurora." Cerbero finds brief.pdf renamed (same hash), layout and copy missing, cover.tif changed keeping size and date. It recovers from the copy matching Delivery 2, not the newest backup. The user confirms set and plan digest; UGOS approves each change. Receipt: three copies verified, delivery complete; a lost raw original is reported apart. An overbroad lesson fails its counterexample; after a restart, the approved revision flags originals without an off-volume copy, citing saved evidence.

## 5. What substantive difference does your idea offer compared with existing tools or conventional AI solutions?

Our implemented name-and-date baseline took each newest copy and mixed versions. Cerbero identifies content by hash, recovers coherent approved sets, counts redundancy by failure domain, separates copies verified from delivery complete, and activates a lesson only with saved evaluation and approval.

## 6. Which UGREEN AI NAS capabilities will be used, and at which step in the workflow?

file-agent: `get-user-dir`, `stat`, `ls`, `find` (scope, exact-size search); `sha256sum` (identity, source and destination checks); `cat` (memory); `mkdir`, `cpmv` copy without overwrite (recovery). document-agent: `qa` (notes as data; rebuilt documents read completely). knowledge-agent: `save-text` (memory, plans, receipts); `answer-official` (guidance).

## 7. What was your technical approach?

`SKILL.md` plus nine references, thirteen delegations, no scripts. Recoveries and rebuilds require a saved, hashed plan confirmed by digest, plus NAS approval per change; paths must resolve inside authorized folders, memory included. Memory is reversible Markdown records via `save-text`, with provenance and revalidation. Cerbero adds no service of its own.

## 8. What is the current development status?

Implemented: Skill 1.2.1 (official checker: zero diagnostics) and a Python lab with simulated experts: 15 scenarios, 151 passing tests, and both review reproductions passing. In simulation the full rules recovered 14/14 required files with no wrong-version claim; the name-and-date baseline made 6. Ten local agent runs following the real `SKILL.md` passed every check, including a policy learned, applied and retired across sessions. Pending: NAS validation of real outputs, save limits and approvals.

## 9. What is your final validation plan?

Core 1: the Aurora incident on the NAS, graded by exporting memory and recovered files. Core 2: a full rebuild whose documents open; a later session applies the learned policy only from saved records. Edge: a source edited after plan approval is never reported verified.

## 10. Are there any known limitations of your Project?

Cerbero acts only when invoked: no monitoring, attack blocking, network isolation, snapshot management or web browsing. Same-NAS hashes are not an independent root of trust. Lab and local agent runs are not device evidence; saves may each need confirmation.

## Third-party components and licenses

Runtime: none; the package is Markdown only and uses UGOS registered experts. Development only, not in the package: Uliya Skill Kit 0.7.3 (UGREEN developer tools agreement), Node.js (MIT), Python standard library (PSF), PyMuPDF (AGPL-3.0, used to render this PDF), pypdf (BSD-3-Clause). AI tools, under the entrant's direction and review: Codex (OpenAI) for research, the product and architecture documents and an independent review of version 1.0.0; Claude Code (Anthropic) for the Skill, lab, agent harness, tests, fixes and documents; Claude subagents played the assistant in local agent runs. Data flows: the Skill adds no service beyond UGOS registered experts, and `answer-official` receives general questions without file data. Where UGOS models and experts process data is not documented and must be checked on the device; no fully local processing is claimed.
