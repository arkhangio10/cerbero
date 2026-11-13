# CERBERO BUNDLE TH-0000-02
- schema: "cerbero-memory-2"
- bundle_id: "TH-0000-02"
- case_id: null
- scope_id: null
- supersedes: null

## RECORD TST-0000-0006
- type: "test-case"
- kind: "similar"
- split: "holdout"
- facts: "Project Borealis: raw/IMG_2002.ARW now has a different digest while its size and modification time are unchanged; raw/IMG_2001.ARW has no copy outside Volume 1."
- expected: "IMG_2002 is reported as altered; IMG_2001 is reported as at risk."
- source: "synthetic test data authorized by the user; fixture P6-similar-borealis-second-raw"

## RECORD TST-0000-0007
- type: "test-case"
- kind: "insufficient"
- split: "holdout"
- facts: "Project Borealis review in which the raw folder returns permission denied for every check."
- expected: "The two raw originals are reported as unknown with open items; no intact, altered or missing claim is made."
- source: "synthetic test data authorized by the user; fixture P7-insufficient-borealis"
