# Recoverability map

The map answers one question: "If this fails, can I rebuild the approved set?" It is a logical graph kept as memory records (assets, versions, copies, locations, domains, approved sets). It is evaluated by reasoning over those records; there is no graph engine or solver on the NAS.

## Relations

- `copy_of`: a copy record holds a version, proven by a digest returned by the NAS.
- `requires`: an approved set requires one specific version of each member asset.
- `located_in`: a copy lies inside a location, by real path.
- `member_of`: a location belongs to a domain (volume, storage pool, device, site), only by user statement or NAS observation with provenance. A domain may have a parent (a volume on a device).
- `supports` / `contradicts`: observations back or challenge a claim.
- `verified_by`: a recovery or rehearsal receipt verified a copy at a time.

## What never establishes independence

Folder names such as "backup" or "archive", different paths, different share names and equal digests. Two locations are independent for a failure only when their recorded memberships say so. A path namespace reported by the NAS (for example a different volume prefix in a real path) is recorded as an observation of the path, not as proof of separate disks: volumes can share a storage pool, and the pool and disks stay unknown unless declared.

## Scenarios

| Scenario | Copies excluded | Copies uncertain |
|---|---|---|
| Location unavailable (L) | copies whose real path is inside the real root of L, including nested folders | copies whose real path was never resolved |
| Domain failure (D) | copies at locations recorded as members of D, directly or through a child domain | copies at locations whose membership for the kind of D, and for every ancestor kind of D, is unknown |

A location is outside the failure of D when it is recorded as a member of a different domain of the same kind, or of a different domain at the kind of any ancestor of D. Example: if volume V1 is recorded on device N1, a location recorded on device U1 is outside a failure of V1, as an inference with both statements as premises.

When the user says "if this location fails" without saying how, evaluate two rows: the location folder becoming unavailable, and the failure of each domain recorded for that location.

## Eligibility

This is the only definition of whether a copy can serve a required version. What-if counts it, and Recover uses it, without a scenario, to choose which recorded copies to re-check. A matching version ID alone never makes a copy eligible. Each condition has three outcomes: it holds, evidence says it fails (the copy is **excluded**), or evidence is missing (the copy is **uncertain**).

| Condition | Holds | Excluded (negative evidence) | Uncertain (missing evidence) |
|---|---|---|---|
| version | the copy record names the required version | it names another version | the version record is missing |
| digest | the recorded copy digest equals the version digest | it differs, or a digest re-observed in this session differs | no digest recorded |
| access | last observation `readable`, or re-observed now | last observation `denied` | `unknown` and not re-observed |
| provenance | `observation` names an observation record, or the copy was re-observed now | | no observation, or a missing one |
| record status | `current` | `superseded` | `needs-review` |
| location | the record names a recorded location and its real path lies inside that location root (see "Paths and scope" in [trust and boundaries](trust-and-boundaries.md)) | the real path is outside, not canonical, or an alias | the location record is missing |
| scenario | the scenario does not reach it | the scenario excludes it | its effect is unknown |

A copy is **eligible** only when every condition holds; excluded when any condition fails; otherwise uncertain. Only eligible copies count as redundancy. An old observation is evidence of what was there then: it keeps the level `modeled`, and a recovery always re-checks the source in the session (D5, then D7) before copying.

## Domain graph checks

Before a domain scenario is evaluated, the recorded memberships and parents of each location are checked. Any of these makes the effect on that location **uncertain**, never unaffected:

- a parent chain that loops back to itself (a cycle);
- a parent or membership naming a domain that is not recorded;
- a membership whose kind differs from the kind recorded for that domain;
- a chain where one kind appears twice, for example a volume whose parent is a volume;
- two memberships that disagree once parents are followed, for example a location recorded on volume V1 and on device U1 when V1 is recorded on device N1.

Report the contradiction and the records involved, and ask the user to correct the declaration.

## Evidence levels

| Level | Meaning |
|---|---|
| rehearsed | a rehearsal receipt verified a copy of this version from this copy, at a stated time |
| verified-now | the copy digest was re-observed in this session |
| modeled | the copy is recorded with a digest from an earlier session; the prediction depends on it still being there |
| insufficient | no copy is eligible and at least one is uncertain: unknown membership or access, missing digest or provenance, a record under review, or a contradictory domain graph |
| none | no recorded copy of the version is eligible or uncertain under the scenario |

The project folder is itself a location: its files that match a version are copies there, and they count like any other copy.

Report the levels separately: "predicted by the model", "copies verified now" and "recovery rehearsed". A rehearsal shows the operations worked at that moment; it does not guarantee future availability.

## Verdicts

Per required version: the number of eligible copies, the number of uncertain copies and the evidence level.

| Set verdict | Condition |
|---|---|
| recoverable | every required version has at least one eligible copy; report the weakest evidence level |
| not-recoverable | some required version has no eligible copy, no uncertain copy, and the inventory of every named location is complete for that version |
| undetermined | neither of the above: name each unknown that blocks the answer |

Counting is by eligible copies, never by locations listed: two copies on one failed volume count as zero for that scenario.

## Inventory completeness

The copy search for a version is complete for a location when its last listing of that location was complete under rule 7 of `SKILL.md` (fewer entries than the limit, truncation reported as absent, no unreadable subfolder), and no later observation showed a change there. The location record keeps this as `inventory`: `complete` or `possibly-incomplete`. Completeness holds only to the listing depth, which the report states. Otherwise the verdict for that version cannot be `not-recoverable`; it is `undetermined`, with the gap named.

## Example (synthetic)

Delivery 2 needs layout v2 and copy v2. Copies: layout v2 in Backup A, copy v2 in Backup A and Backup B. The user stated that the project and Backup A are on volume V1 and that Backup B is on V1 too. Backup C has no stated volume or device.

| Scenario | layout v2 | copy v2 | Verdict |
|---|---|---|---|
| Project folder unavailable | 1 eligible (Backup A), modeled | 2 eligible, modeled | recoverable (modeled) |
| Volume V1 failure | 0 eligible | 0 eligible | not-recoverable |
| Volume V1 failure, with a copy of layout v2 in Backup C | 0 eligible, 1 uncertain | 0 eligible | not-recoverable: copy v2 has no copy outside V1; layout v2 would stay undetermined |

## Rehearsal

A rehearsal is a Recover run into a new rehearsal folder, approved like any recovery, that leaves the source copies untouched. Verified entries raise those copies to `rehearsed`. Nothing is deleted or disconnected to evaluate a scenario.
