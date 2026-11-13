bash nas.sh delegate --target knowledge-agent --instruction 'Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-IDX-0002-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: # CERBERO BUNDLE IDX-0002-01
- schema: "cerbero-memory-2"
- bundle_id: "IDX-0002-01"
- case_id: "CAS-0002"
- scope_id: "SCP-0001"
- supersedes: null

## RECORD IDX-0002-01-0001
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-B-0001-01.md"
- bundle_id: "B-0001-01"
- sha256: "682855fb8e2e81be54754163486d42504ac98e272ed3d002cef9a7ae8cd62259"
- status: "current"

## RECORD IDX-0002-01-0002
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-IDX-0001-01.md"
- bundle_id: "IDX-0001-01"
- sha256: "4cf8bbe0ec55f7ec826eb8c5ceba33f042467747e2c07d7b88ba977f86ec7e0b"
- status: "superseded"

## RECORD IDX-0002-01-0003
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-B-0002-01.md"
- bundle_id: "B-0002-01"
- sha256: "b6b2819e543fbe84378321956f51001da7ff5622cda1eb6db0b015361e5e1c1f"
- status: "current"

## RECORD IDX-0002-01-0004
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-B-0002-02.md"
- bundle_id: "B-0002-02"
- sha256: "3610a53ae8d4847f507e14ee0f6db1dfee2f96ccca1951f9fe5ce58726d67dec"
- status: "current"
'
