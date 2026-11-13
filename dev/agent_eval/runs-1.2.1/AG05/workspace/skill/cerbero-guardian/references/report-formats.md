# Report formats

Every report starts with one plain result line, then a review header, and ends with coverage. Use the user language for prose; keep IDs, statuses, digests and paths unchanged. Show digests as their first and last four characters plus the record ID that holds the full value.

## Plain result line

The first line states the outcome in words the user can act on without reading digests, built only from results the report shows. A delivery is called complete only when the receipt says so. For example:

- "5 of 5 delivery files rebuilt and verified; one original outside the delivery has no copy."
- "3 copies verified, but the delivery is incomplete: brief.pdf could not be checked."
- "Nothing was created or copied: you declined plan PLN-0004-01."
- "Delivery 2 could not be rebuilt if Volume 1 failed: every copy is on that volume."

## Review header

```text
Cerbero review of {project_root}
Mode: Investigate | What-if | Baseline | Recover | Learn
This review: what it covered and when it ran (time as returned by the NAS, or unknown)
Previous review: case ID and coverage, or none
Active policies applied: policy record, version, frozen rule digest, evaluation and approval, or none
Memory: files current, files needing review, newest index, whether the listing was complete
```

## What-if

| Required version | Eligible copies | Uncertain copies | Evidence level | Why |
|---|---|---|---|---|
| layout.indd v2 | 0 | 0 | none | only copies are on volume V1 (STM-0001-0006) |

Then three separate lines: predicted by the model, copies verified now, recovery rehearsed before (historical, with the receipt). Then the set verdict and every unknown that blocks a firmer answer.

## Case summary

| Asset | State | Evidence | Next step |
|---|---|---|---|
| brief.pdf | moved, now at {project_root}/brief-FINAL.pdf | digest equal to v2 (OBS-0003-0004) | none; cause unknown |
| cover.tif | altered, same size and time | digest differs from v2 (OBS-0003-0007) | recover v2 |
| raw/DSC_0142.ARW | missing | no copy in 3 named locations (OBS-0003-0011..0013) | not recoverable with available sources |

Then open hypotheses, contradictions, findings (quoted), coverage and "Cause: unknown" unless a cited source states one.

## Recovery plan

| Entry | Asset | Expected version | Source (re-observed) | Destination |
|---|---|---|---|---|

Then the target approved set with its members, versions, record file and approving statement (or "no prior reference: fidelity to the chosen sources only"), preconditions, success conditions, pending and out-of-scope items, risks, the plan ID and the saved plan digest, followed by one question: "Do you confirm approved set {set name} and approve plan {plan_id} with digest {digest}?" Without a prior reference: "Do you approve plan {plan_id} with digest {digest}, knowing it can only check fidelity to the sources you chose?"

## Receipt

| Entry | File | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|---|

Then two separate lines, never merged: the result of the copies ("3 copies verified") and the delivery ("delivery complete", or "delivery incomplete:" with every pending member by name and why). Then the reference (approved versions, or fidelity to the chosen sources only), files failed and out of scope by name, the changed files outside the requested target with whether a copy exists, what verification was possible for each `fidelity-only` entry, and where the receipt was saved, or that it could not be saved.

## Rebuild manifest

| File | Version | Provenance | Bytes | Approved version | Format check |
|---|---|---|---|---|---|
| brief.pdf | VER-0001-0001 | original in the project, moved to brief-FINAL.pdf | equal to source | equal | opened by document-agent, whole file |
| cover.tif | VER-0001-0003 | copy in backups/aurora-2026-10-01 | equal to source | equal | not available for .tif |

Then the rebuild folder, the delivery line, and: "Equal digests show equal bytes. They do not show that malware is absent; a format check shows that a document opened, not that its content is the one you want."

## Policy evaluation

| Case | Split | Kind | Expected | Replayed | Result |
|---|---|---|---|---|---|

Then the guard result, the frozen rule digest, development and holdout results separately, whether the holdout cases were unseen before the freeze, and the question: "Do you approve policy {policy_id} version {version}?"

In a later review, each policy that changed a result is named with its evidence: "raw/DSC_0101.ARW reviewed as critical because of policy POL-0004-0003 v2 (frozen digest c6e3...8219, evaluation EVL-0004-0002 with holdout cases, approved by you)". A policy that is not applied is named with the reason.

## Coverage block

```text
Assets checked by digest: N of M critical; ordinary checked by metadata: K
Listings: L complete, T truncated (named), U folders unreadable (named)
Digests computed: D files, B bytes when sizes are known
Not reviewed: named items or counts
Out of scope: paths rejected by the scope rules, with the reason
Memory needing review: files not listed in the index, changed, or unreadable
Not persisted: records whose save was declined or failed
```
