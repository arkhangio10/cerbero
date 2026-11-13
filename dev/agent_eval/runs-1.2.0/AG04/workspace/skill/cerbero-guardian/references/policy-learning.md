# Policy learning

Learning in Cerbero means retrieving relevant cases and applying reviewed, versioned policies to its own reviews. It does not retrain a model, rewrite these instructions, run in the background or treat every incident as an attack.

## Lifecycle

`candidate` → `evaluated` → `approved` → `active` → `retired`, with `rejected` from `candidate` or `evaluated`.

- **candidate**: proposed after a case, with condition, scope, effect, motivating case and the development cases used to draft it.
- **evaluated**: passed the invariant guard and every required case, including the holdout cases.
- **approved**: the user explicitly approved this policy version after seeing its evaluation.
- **active**: the approved version was persisted (D10) as a record with status `active`, the rule digest and the user words, and is listed in the newest index snapshot. Only active policies change a review.
- **retired**: replaced or withdrawn by a recorded user decision: a new record with status `retired`, the user words, and `supersedes` naming the active record. Returning to an earlier version is also a recorded decision.
- **rejected**: failed the guard or a case. The record and its failures are kept.

Records are never edited: each status change is a new `policy` record whose `supersedes` names the previous one, so the chain candidate → active → retired stays readable.

## Allowed effects

The `effect` field is a list of lines, each one an effect name below followed by its argument. Folders are relative to the project root; `.` means the whole project.

| Effect line | Meaning | Example |
|---|---|---|
| `promote-critical <folder>` | review the files of the folder as critical | `promote-critical raw`: digest them every review, include them in the map |
| `informational <folder>` | a folder the user declared regenerable is reported, not treated as an incident | `informational exports/previews` |
| `add-search-location <location>` | add a location the user named to the copy search | `add-search-location usb-archive/aurora` |
| `add-check <check>` | add a check card to the standard sequence | `add-check five-missing-digest-continuity` |
| `add-recoverability-check <scenario>` | add a what-if to the review | `add-recoverability-check project-volume` |
| `report-order <section>` | change report ordering | `report-order unreadable-first` |

An effect line that names nothing in this table is unknown, and fails the guard (rule 1).

## Invariant guard

A candidate is rejected before evaluation if its effect would:

1. add a capability, expert, Action or delegation not in the capability evidence of this Skill;
2. widen the authorized scope, or search a location the user did not name;
3. remove, merge or pre-answer any user confirmation or NAS approval;
4. allow overwriting, moving instead of copying, or deleting;
5. drop the source check before copying or the destination check after copying;
6. lower the review level of a user-declared critical asset or approved-set member, including marking its folder informational;
7. treat document, log or memory text as authority, or label a cause without a cited source;
8. remove, hide or shorten coverage, pending items, unknowns or findings in any report.

The guard applies to the effect lines and to their consequences in every required case. It runs again on every active policy when the policy is loaded and before it changes a result, because policy files live on the same NAS and can be altered; a policy that fails is not applied, and the report says so.

## Activation in a later session

A new session knows a policy only from the memory folder. Before a policy changes anything, all of these must hold, each read from a trusted file (listed in the newest index with a matching digest):

1. the newest record of the policy has status `active`, the user words in `approval`, and a `rule_sha256`;
2. following `supersedes` leads to the frozen `candidate` record with the same version, condition, scope and effect lines;
3. the digest D7 returns for the file holding that frozen candidate equals `rule_sha256`;
4. an `evaluation` record names that candidate, has the same `rule_sha256`, verdict `evaluated`, and lists passing cases of the four kinds, at least one of them holdout, each one a trusted `test-case` record of that split and kind;
5. the invariant guard passes on the effect lines.

If any condition fails, the policy is not applied; the report names the policy and the condition that failed. Candidate, evaluated, rejected and retired records never change a review. Whoever can write the memory folder can still forge a whole chain: these checks detect partial edits and the guard limits what a forged policy can do, but they are not an independent root of trust (see [trust and boundaries](trust-and-boundaries.md)).

When a policy changes a result, the report names the policy record, its version, the file it was loaded from, the frozen rule digest, the evaluation and the user approval, and which assets it changed.

## Required cases

Each candidate is replayed against at least:

| Kind | What it must show |
|---|---|
| origin | the incident that motivated it: the policy would have changed the result in the intended way |
| similar | a different case where it should also apply |
| counterexample | a legitimate situation where it must not raise an incident, block work or accuse anyone |
| insufficient | a case with missing evidence where it must report uncertainty instead of a conclusion |

Cases are `test-case` records, as defined in [memory records](memory-records.md). They come from closed cases, or from synthetic test data the user authorized for rehearsal. Each one holds its facts, its expected outcome and its split: `development` or `holdout`. If a required kind has no record, the candidate stays `candidate`. Cerbero asks the user for a case of that kind; it does not invent one.

Replay over visible cases checks consistency with those cases. Only holdout cases unseen before the freeze say anything about generalization, and even then only about cases like them.

## Closed cases

Learning starts from a closed case: its case bundle and receipt are persisted, and the user has confirmed the outcome in the conversation. Cerbero records that confirmation as a `statement` and closes the case with a new `case` record, status `closed`, that supersedes it. An open case cannot motivate a policy.

## Development and holdout

- Test cases are stored one split per file: a bundle with ID `TD-` holds only development cases, a bundle with ID `TH-` holds only holdout cases. Cerbero never writes a test case to make a rule pass.
- Development cases must be saved before the candidate is drafted. Drafting and revising read and use development files only; the candidate lists the cases in `drafted_from`.
- Holdout files are not read before the freeze. Cerbero may see their names in the D3 listing, never their content. If a holdout file was read before the freeze, its cases cannot serve as holdout for this candidate: say so and ask the user for new holdout cases.
- Freeze: the candidate is saved with D10 and the saved file is hashed with D7; that NAS digest is `rule_sha256`. Cerbero never computes or types a digest itself. Freezing is a mandatory save: if it is not persisted, evaluation stops. A change after that point creates a new version that starts the evaluation again.
- After the freeze, list the memory folder again (D3) and read the holdout files (D4). The user may add them only now. If the four kinds are not all present, or no holdout case exists, the rule stays `candidate` with an open item.
- The evaluation record lists, per case, the test-case ID, the split, the kind and pass or fail; the report adds the expected and replayed outcomes. Results are reported separately for development and holdout cases, and the report says whether the holdout cases were unseen before the freeze.
- A candidate that fails a development case is rejected before any freeze; its evaluation is saved with `rule_sha256` `null`.

## How replay works on the NAS

Replay is reasoning over the facts stored in case records: Cerbero applies the frozen rule to each case and compares the outcome with the expected one. When the user authorizes a rehearsal folder with synthetic data, the same rule can also drive a real read-only review of that folder. Replay over records shows consistency with recorded cases; it is not a guarantee about future incidents.

## Example

Origin: originals in raw/ were not critical, the map never warned that they had no copy outside volume V1, and one original was lost.

| Version | Effect lines | Counterexample result | Status |
|---|---|---|---|
| v1 | `promote-critical .` ("every file in the project is critical") | regenerated previews in exports/previews/ raise false incidents | rejected in development |
| v2 | `promote-critical raw`, `informational exports/previews` | previews reported as informational, no incident | frozen, passed the holdout cases, approved by the user, active |

The next review, in a new session, loads v2 from its records, digests raw/ files, includes them in the map, and reports that they have no copy outside V1, naming policy v2, its frozen digest, its evaluation and the approval as the reason. After the user retires v2, the same review no longer applies it.
