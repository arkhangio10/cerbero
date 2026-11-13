import json

M = "/data/studio/cerbero-memory/"
entries = [
    ("CERBERO-B-0001-01.md", "B-0001-01", "8056343e9b83127a3cfa50579196f5d4787f2ac405c42be8b2a44bb186af1931", "current"),
    ("CERBERO-B-0001-02.md", "B-0001-02", "bd00bb36e319d96ffd5a0b49353544a3d74c09d8d7f9fe7706b8c0e14d99d758", "current"),
    ("CERBERO-IDX-0001-01.md", "IDX-0001-01", "2f38a8093b55bc73033c33558d887da934b14073b413411e28469afb32ad35cc", "superseded"),
    ("CERBERO-B-0002-01.md", "B-0002-01", "52c4ab514eb4604a9cbcc9b9aa919ac79870b3293d269c15ef084319404ae4d4", "current"),
    ("CERBERO-B-0002-02.md", "B-0002-02", "1b60af11c336b2ff8ab3d856a01c06249f32430e333658cdde9caf62faf8088f", "current"),
]
lines = [
    "# CERBERO BUNDLE IDX-0002-01",
    '- schema: "cerbero-memory-2"',
    '- bundle_id: "IDX-0002-01"',
    '- case_id: "CAS-0002"',
    '- scope_id: "SCP-0001"',
    "- supersedes: null",
]
for n, (f, bid, sha, st) in enumerate(entries, 1):
    lines += [
        "",
        f"## RECORD IDX-0002-01-{n:04d}",
        '- type: "index-entry"',
        f"- file: {json.dumps(M + f)}",
        f"- bundle_id: {json.dumps(bid)}",
        f"- sha256: {json.dumps(sha)}",
        f"- status: {json.dumps(st)}",
    ]
text = "\n".join(lines) + "\n"
prefix = "Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-IDX-0002-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: "
with open("scratch/idx-0002-01.md", "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
with open("scratch/d10_idx.txt", "w", encoding="utf-8", newline="\n") as fh:
    fh.write(prefix + text)
print(len(text.encode("utf-8")))
