# CERBERO BUNDLE TH-0000-01
- schema: "cerbero-memory-2"
- bundle_id: "TH-0000-01"
- case_id: null
- scope_id: null
- supersedes: null

## RECORD TST-0000-0003
- type: "test-case"
- kind: "similar"
- split: "holdout"
- facts: "Project Borealis: raw/IMG_2001.ARW now has a different digest while its size and modification time are unchanged; raw/IMG_2002.ARW has no copy outside Volume 1."
- expected: "IMG_2001 is reported as altered; IMG_2002 is reported as at risk."
- source: "synthetic test data authorized by the user; fixture P3-similar-borealis"

## RECORD TST-0000-0004
- type: "test-case"
- kind: "insufficient"
- split: "holdout"
- facts: "Project Aurora review in which the raw folder returns permission denied for every check."
- expected: "The three raw originals are reported as unknown with open items; no intact or missing claim is made."
- source: "synthetic test data authorized by the user; fixture P4-insufficient"

## RECORD TST-0000-0005
- type: "test-case"
- kind: "similar"
- split: "holdout"
- facts: "Project Aurora: raw/DSC_0150.ARW is missing; an identical copy exists on the external USB archive (device usb-1); the other raw originals have no copy."
- expected: "DSC_0150 is reported missing but not at risk; DSC_0101 and DSC_0142 are at risk; the preview is not at risk."
- source: "synthetic test data authorized by the user; fixture P5-similar-copy-exists"
