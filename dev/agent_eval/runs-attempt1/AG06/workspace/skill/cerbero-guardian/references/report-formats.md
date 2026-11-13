# Report formats

Every report starts with a review header and ends with coverage. Use the user language for prose; keep IDs, statuses, digests and paths unchanged. Show digests as their first and last four characters plus the record ID that holds the full value.

## Review header

```text
Cerbero review of {project_root}
Mode: Investigate | What-if | Baseline | Recover | Learn
This review: what it covered and when it ran (time as returned by the NAS, or unknown)
Previous review: case ID and coverage, or none
Active policies applied: policy IDs and versions, or none
```

## What-if

| Required version | Eligible copies | Uncertain copies | Evidence level | Why |
|---|---|---|---|---|
| layout.indd v2 | 0 | 0 | none | only copies are on volume V1 (STM-0001-0006) |

Then three separate lines: predicted by the model, copies verified now, recovery rehearsed. Then the set verdict and every unknown that blocks a firmer answer.

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

| Entry | Status | Source digest before | Destination digest | Note |
|---|---|---|---|---|

Then: overall status, the reference (approved versions, or fidelity to the chosen sources only), whether the target set is complete, files verified, failed, out of scope and pending by name, what verification was possible for each `fidelity-only` entry, and where the receipt was saved, or that it could not be saved.

## Policy evaluation

| Case | Split | Kind | Expected | Replayed | Result |
|---|---|---|---|---|---|

Then the guard result, the frozen rule digest, development and holdout results separately, and the question: "Do you approve policy {policy_id} version {version}?"

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
