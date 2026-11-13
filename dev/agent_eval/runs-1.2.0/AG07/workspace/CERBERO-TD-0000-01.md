# CERBERO BUNDLE TD-0000-01
- schema: "cerbero-memory-2"
- bundle_id: "TD-0000-01"
- case_id: null
- scope_id: null
- supersedes: null

## RECORD TST-0000-0001
- type: "test-case"
- kind: "origin"
- split: "development"
- facts: "Review of project Aurora before the incident. raw/DSC_0101, raw/DSC_0142 and raw/DSC_0150 are ordinary assets with no recorded copy outside Volume 1. exports/previews/cover-preview.jpg has no copy and the user declared that folder regenerable."
- expected: "The review reports the three raw originals as at risk under a Volume 1 failure and does not report the preview as at risk."
- source: "synthetic test data authorized by the user; fixture P1-origin"

## RECORD TST-0000-0002
- type: "test-case"
- kind: "counterexample"
- split: "development"
- facts: "exports/previews/cover-preview.jpg has a new digest and modification time after the export tool regenerated it; the user declared exports/previews regenerable."
- expected: "The preview change is reported as informational. No incident, no recovery and no at-risk flag for the preview."
- source: "synthetic test data authorized by the user; fixture P2-counterexample"
