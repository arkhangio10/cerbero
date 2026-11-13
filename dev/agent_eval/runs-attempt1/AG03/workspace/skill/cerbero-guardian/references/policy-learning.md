# Policy learning

Learning in Cerbero means retrieving relevant cases and applying reviewed, versioned policies to its own reviews. It does not retrain a model, rewrite these instructions, run in the background or treat every incident as an attack.

## Lifecycle

`candidate` → `evaluated` → `approved` → `active` → `retired`, with `rejected` from `candidate` or `evaluated`.

- **candidate**: proposed after a case, with condition, scope, effect, motivating case and the development cases used to draft it.
- **evaluated**: passed the invariant guard and every required case, including the holdout cases.
- **approved**: the user explicitly approved this policy version after seeing its evaluation.
- **active**: the approved version was persisted (D10) and is listed in the newest index snapshot. Only active policies change a review.
- **retired**: replaced or withdrawn by a recorded user decision. Returning to an earlier version is also a recorded decision.
- **rejected**: failed the guard or a case. The record and its failures are kept.

## Allowed effects

| Effect | Example |
|---|---|
| promote folders or assets to critical review | "files under raw/ are critical: digest every review, include them in the map" |
| mark a folder the user declared regenerable as informational | "changes under exports/previews/ are reported, not treated as incidents" |
| add a named location to the copy search | "also search the archive share the user named" |
| add a check card to the standard sequence | "when five or more assets are missing, run the in-scope digest continuity check before any classification" |
| add a recoverability check to the review | "after each review, evaluate the approved sets under a failure of the project volume" |
| change report ordering | "list unreadable folders first" |

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

The guard applies to the effect text and to its consequences in every required case. It runs again on every active policy when the policy is loaded and before it changes a result, because policy files live on the same NAS and can be altered; a policy that fails is not applied, and the report says so.

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

Learning starts from a closed case: its case bundle and receipt are persisted, and the user has confirmed the outcome in the conversation. An open case cannot motivate a policy.

## Development and holdout

- Test cases are stored one split per file: a bundle with ID `TD-` holds only development cases, a bundle with ID `TH-` holds only holdout cases. Cerbero never writes a test case to make a rule pass.
- Development cases must be saved before the candidate is drafted. Drafting and revising read and use development files only; the candidate lists the cases in `drafted_from`.
- Holdout files are not read before the freeze. Cerbero may see their names in the D3 listing, never their content. If a holdout file was read before the freeze, its cases cannot serve as holdout for this candidate: say so and ask the user for new holdout cases.
- Freeze: the candidate is saved with D10 and the saved file is hashed with D7; that NAS digest is `rule_sha256`. Cerbero never computes or types a digest itself. Freezing is a mandatory save: if it is not persisted, evaluation stops. A change after that point creates a new version that starts the evaluation again.
- After the freeze, list the memory folder again (D3) and read the holdout files (D4). The user may add them only now. If the four kinds are not all present, or no holdout case exists, the rule stays `candidate` with an open item.
- The evaluation record lists, per case, the split, the kind, the expected outcome, the replayed outcome and pass or fail. Results are reported separately for development and holdout cases, and the report says whether the holdout cases were unseen before the freeze.

## How replay works on the NAS

Replay is reasoning over the facts stored in case records: Cerbero applies the frozen rule to each case and compares the outcome with the expected one. When the user authorizes a rehearsal folder with synthetic data, the same rule can also drive a real read-only review of that folder. Replay over records shows consistency with recorded cases; it is not a guarantee about future incidents.

## Example

Origin: originals in raw/ were not critical, the map never warned that they had no copy outside volume V1, and one original was lost.

| Version | Rule | Counterexample result | Status |
|---|---|---|---|
| v1 | "every file in the project is critical; any change is an incident" | regenerated previews in exports/previews/ raise false incidents | rejected |
| v2 | "files under raw/ are critical; exports/previews/, declared regenerable by the user, is informational" | previews reported as informational, no incident | evaluated, then approved by the user, then active |

The next review digests raw/ files, includes them in the map, and reports that they have no copy outside V1, naming policy v2 as the reason.
