# Devpost submission fields (copy and paste)

Prepared for the UGREEN Hackathon 2026 form. Fields marked "you" need the entrant's own answer.

## Project overview

**Project name** (60 characters max):

```text
Cerbero: recover the right version, prove it, learn safely
```

**Elevator pitch** (200 characters max):

```text
A UGREEN AI NAS Skill that finds what changed in a project, recovers or rebuilds the approved versions with hash proof and a receipt, and adopts lessons only after counterexamples fail to break them.
```

## Project details (public page)

**About the project** (Markdown):

```markdown
## Inspiration

A small creative studio keeps its originals and client deliveries on a NAS. When files vanish or change, nobody knows
what changed, which copy holds the version the client approved, or whether the backups really cover a delivery. Taking
the newest copy of each file mixes versions: the layout from Monday, the cover from Friday.

## What it does

Cerbero (`cerbero-guardian`) answers three questions about the folders you authorize:

- **Guardian:** if this folder or volume failed, could I still rebuild the approved delivery?
- **Investigator:** what changed, according to the evidence?
- **Rescuer:** recover, or fully rebuild, the right versions into a new folder, with proof.

It identifies content by SHA-256, not by name or date. Before any copy it saves a plan, shows you its digest, and acts
only after you confirm that exact plan and the NAS approves each change. The receipt keeps two facts apart: how many
copies were verified, and whether the delivery you asked for is complete. A lesson from an incident becomes an active
policy only after it passes test cases it never saw while it was written, and a later session applies it only from its
saved, verified records.

## How we built it

- An orchestration Skill: `SKILL.md` plus nine Markdown references, thirteen delegations to UGOS registered experts
  (`file-agent`, `document-agent`, `knowledge-agent`), no scripts. It passes the official checker with zero diagnostics.
- A local Python lab, never shipped, that simulates the experts, runs 15 scenarios with memory reloaded only from saved
  files, and compares Cerbero with a name-and-date baseline.
- An agent harness in which a model follows the real `SKILL.md` against simulated experts and a scripted user; an
  evaluator binds every change to the exact plan the user approved.

## Challenges we ran into

- Making "recoverable" honest: copies on the same volume are not independent, and an incomplete listing can never prove
  that something is gone.
- Binding approvals to evidence: two independent reviews found ways a run could look correct without being so; each was
  fixed with a regression test.
- Memory the model writes must survive restarts and tampering: an edited or planted file never silently changes an
  approved set, a copy or a policy.

## Accomplishments that we're proud of

- In the lab, Cerbero recovered 14 of 14 required files with the right version; the name-and-date baseline made 6
  wrong-version claims.
- A full rebuild of a delivery with a manifest that keeps bytes, version and format checks apart.
- In ten local runs, model agents following the real `SKILL.md` passed every check of an evaluator that binds each
  change to the exact plan the user approved, including a learning cycle run only by agents: a rule rejected by a
  holdout case, revised, tested on new holdout cases, activated, applied by a new session and then retired.

## What we learned

Most recovery mistakes come from treating a name, a date or "it is in the backup folder" as proof. Separating what was
observed from what was inferred, and saying so in every report, matters more than any single algorithm.

## What's next

- Validate on a UGREEN AI NAS: real expert outputs, save limits, approvals and timings. Nothing has run on a device yet.
- A minimal hardening plan and an independent emergency copy of Cerbero's memory.
- Protected exports: encrypted, revocable copies of delivered files with audited access. A local prototype exists outside
  the Skill; it is not part of the submitted package and has not run on a NAS.

Limits we state openly: Cerbero acts only when invoked; it does not monitor, block attacks or manage snapshots; hashes
kept on the same NAS are not an independent root of trust; and lab and local agent runs are not device evidence.
```

**Built with** (tags):

```text
ugreen-ai-nas, ugos, uliya-skill-kit, markdown, sha-256, python, unittest, node.js, pymupdf, claude-code
```

**"Try it out" links:** none required. Add a repository link only if you publish one (it must be in English and hold no
secrets; `dev/out/` and the virtual environment are already ignored).

**Image gallery and thumbnail:** `submission/media/` (3:2 PNG).

**Demo video URL:** optional in round 1 (the official FAQ says no video is required at this stage). The final requires a
video of the Skill running on the NAS.

## Additional info (judges and organizers)

| Field | Value |
|---|---|
| Skill package (ZIP) | `dist/cerbero-guardian-1.2.1.zip` (10 Markdown files, 46,818 bytes) |
| Submitter type | you |
| Country of residence | you |
| Track | Open Innovation |
| Development start date (MM-DD-YY) | you: the earliest project files are dated 11-09-26 |
| PDF | `submission/cerbero-guardian-proposal.pdf` |
