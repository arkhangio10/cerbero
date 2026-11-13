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
- sha256: "22d927d38eabd5a2be1748dc9df31b3e09a4b524db937a5f386771d06dc1e19a"
- status: "current"

## RECORD IDX-0002-01-0002
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-IDX-0001-01.md"
- bundle_id: "IDX-0001-01"
- sha256: "a3d040488be4350c408b1ebcd679f6cfbde3e7add74343ac9b45ff4bc5100918"
- status: "superseded"

## RECORD IDX-0002-01-0003
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-B-0002-01.md"
- bundle_id: "B-0002-01"
- sha256: "bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569"
- status: "current"

## RECORD IDX-0002-01-0004
- type: "index-entry"
- file: "/data/studio/cerbero-memory/CERBERO-B-0002-02.md"
- bundle_id: "B-0002-02"
- sha256: "5ea2dc2bfbaa045c34b2c0b26268e4586e130a76b7fd6e960bf0994a65b6f3ac"
- status: "current"
'
