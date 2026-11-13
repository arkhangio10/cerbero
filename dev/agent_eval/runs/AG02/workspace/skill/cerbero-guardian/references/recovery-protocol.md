# Recovery protocol

The Rescuer recovers versions of one approved set into a new folder, binds the work to a saved plan the user approved, checks each source before copying and each destination after, and records a receipt. Recovery without a prior reference follows the same protocol.

## Source selection

1. The target is an approved set chosen by the user. Cerbero shows its members, versions, record file and approving statement; memory alone never decides what is recovered. The user reconfirms the set in the same reply that approves the plan. The members to recover are those classified `missing` or `altered`; members `moved` inside the scope are reported with their new path and are not copied; members `unknown` stay pending. Assets outside every approved set that are `missing` or `altered` are recovered to their recorded version, under the same rules.
2. Candidate sources for a member are recorded copies of the required version in the locations the user named in this session, chosen with the eligibility rules of [recoverability map](recoverability-map.md): an excluded copy is never read; an uncertain one may be re-checked. Prefer the location that provides the most members of the set, then fewer locations overall; never choose by recency.
3. Re-check each chosen candidate: its recorded path must pass "Paths and scope" in [trust and boundaries](trust-and-boundaries.md) against the real root of its location as resolved now; D5 must return a real path inside that root; only then D7, with the expected digest. If the digest no longer matches, record the contradiction, mark dependent records `needs-review` and try the next candidate, then search the other named locations with an exact size filter (D6) and digests (D7) of entries whose real paths are inside the location.
4. If the set cannot be completed, show which members have no eligible source and wait for the user (`waiting_user`) to choose: recover the available members of the target set as a partial recovery, recover another approved set that is complete, or stop. Never combine versions of different sets, and never fill a gap with an unapproved version.

## Plan contract

A plan record and one plan-entry record per file, saved with D10. Case records not yet saved go in the same bundle, so one save covers them. The saved file is hashed with D7; the plan ID with that digest identifies exactly what the user approves.

```text
Goal: recover approved set SET-0001-0002 (Delivery 2) members layout.indd, copy.docx, cover.tif
Reference: approved-version (or source-fidelity when there is no prior reference)
Expected versions: VER-0001-0002 (sha256 ...), VER-0001-0003 (sha256 ...), VER-0001-0004 (sha256 ...)
Sources: real paths of eligible copies, each re-observed in this session
Destinations: {recovery_folder} followed by the path of the asset inside the project, both checked for scope
Operations: create {recovery_folder}; copy each source to its destination, never move, never overwrite
Preconditions per entry:
  - the user approved this plan ID and digest, and the target set it names
  - the operation exists in the capability evidence and the expert reports it allowed
  - the source real path lies inside its authorized root, and its digest, observed again immediately before copying, equals the expected digest
  - the destination does not exist and lies inside the recovery folder
Success conditions per entry:
  - the destination exists at the planned real path returned by the NAS
  - its digest equals the expected digest
Pending items and risks: members with no source, unknown coverage, sources that may change, no atomic copy
```

The plan is a mandatory save. If the save is declined, fails, is not verified, returns no path, returns a path outside the memory folder, or the saved file cannot be hashed, the recovery stops there: no folder is created and nothing is copied. The receipt says why, with overall `cancelled` when the user or the NAS declined the save and `failed` otherwise, and it carries the unsaved plan records so the user can see what was not executed.

## States

Plan: `draft` → `backed` (every entry has a re-observed source) → `approved` (user confirmed plan ID and digest) → `executing` → `verified`, `fidelity-only`, `partial`, `failed`, `cancelled` or `invalidated`.

A change to a source, destination, scope, target set or the plan text invalidates the affected part; a new revision with a new digest needs a new confirmation. Immediately before the first change, the saved plan file is hashed again with D7; a different digest stops execution as `invalidated`.

## Execution per entry

| Step | Check | On failure |
|---|---|---|
| E1 | D5 shows the destination absent; D7 on the source equals the expected digest | destination exists: go to the retry rule; source differs or is unreadable: `invalidated-source-changed`; source real path outside its root: `out-of-scope` |
| E2 | D12 copy returns `completed` with a real destination path equal to the planned one | `failed-copy`; `cancelled` if approval was declined; `destination-differs` if the NAS placed the copy at another path or returned none |
| E3 | D7 on the real destination path equals the expected digest | `failed-verification`; then D7 on the source again: if it changed, `invalidated-source-changed` |

Entry statuses: `verified`, `already-present-verified`, `failed-copy`, `failed-verification`, `invalidated-source-changed`, `conflict-destination-exists`, `destination-differs`, `no-source`, `fidelity-only`, `cancelled`, `not-attempted`, `out-of-scope`.

An entry whose destination would leave the recovery folder, or whose recorded path is not inside the project, is `out-of-scope` before the plan is saved: it is listed as pending and not executed.

A `destination-differs` entry is hashed where the NAS put it when that place is inside the recovery folder, and reported with that path, but stays pending: a new plan revision decides the destination. Because `cpmv` may treat a destination as a folder, the plan always states a full destination path.

A destination that fails verification stays where it is, marked unverified; it is never promoted to an approved version, and cleaning it up needs its own scope and approval.

## Receipt

The receipt names the plan ID and digest, and the approval decision with the user words. For every entry it gives the plan entry it executes, the asset and version, the status, the real destination path, and the source digest before, the destination digest and the source digest after when observed. It adds coverage and pending items. Overall status:

- `verified`: every entry of the plan is `verified` or `already-present-verified`.
- `fidelity-only`: every entry is `fidelity-only`; no prior reference existed (see below).
- `partial`: at least one entry succeeded and at least one did not.
- `failed`: no entry succeeded.
- `cancelled`: the user or the NAS declined before any copy.
- `invalidated`: the plan changed before execution.
- `not-needed`: nothing in the target set had to be recovered.

When no entry can be executed (every needed member has no source or is out of scope, or nothing needs recovery), nothing is created, no plan confirmation is asked, and the receipt is saved together with a plan revision that has no entries and lists the pending members. Every receipt therefore names a plan record that exists.

The receipt also states whether the target set is complete: complete only when every required member is intact, moved inside the scope with a matching digest, or verified in the recovery folder. A receipt is a checkable record, not a forensic certification and not proof that malware is absent. A receipt that cannot be saved is shown in full in the conversation.

## Retry after a partial result

A retry is a new plan revision that names the previous receipt and the plan it supersedes, and needs a new confirmation. It reuses the recovery folder of that receipt: D11 is not sent for it; D5 confirms the folder still exists at the same real path. If it does not, the retry stops with overall `failed` and Cerbero proposes a new plan with a new folder. For each entry:

- destination exists and matches the expected digest: `already-present-verified`, not copied again;
- destination exists and does not match: `conflict-destination-exists`; stop that entry and ask for a new destination folder;
- destination absent: run E1 to E3 again with a fresh source check.

No atomicity, exactly-once execution or automatic rollback of a whole set is claimed.

## Rehearsal

A rehearsal checks that a set can actually be rebuilt. Its plan includes every member of the set, not only changed ones, sourced from copies outside the location or domain being evaluated, into a new folder named `cerbero-rehearsal-` followed by the case ID. It follows the same confirmations, checks and receipt. Verified entries raise those copies to the `rehearsed` level. Sources are only read.

## Without a prior reference

When memory holds no approved digest for a file, Cerbero can still copy a source the user names, with the same plan, approval and receipt:

1. The source path must lie inside a folder the user named; D5 must return its real path inside that folder.
2. D7 observes the source digest now; that digest is the expected digest of the plan entry, and the plan records `reference: source-fidelity`.
3. Save and hash the plan (mandatory), show its ID and digest, and wait for the user confirmation. A refusal stops everything: no folder, no copy, receipt `cancelled`.
4. Execute E1 to E3. A destination whose digest equals the source digest observed before the copy is `fidelity-only`, never `verified`.

The receipt overall is `fidelity-only` and says that the copy is faithful to the chosen source, and that whether that source is the version the user expects could not be checked against any earlier reference.

## When no source exists

Report the set or member as not recoverable with the sources available, list every location and coverage searched, and create no file. Suggest only supported next steps: name another location the NAS can read, or ask official guidance (D9). Cerbero does not promise recovery without copies, decryption without keys or physical disk recovery.

## Recycle bin

`restore` is not used in this version. If a location the user names lists a recycle-bin path with a matching digest, it is treated like any other copy: copied, never restored in place.
