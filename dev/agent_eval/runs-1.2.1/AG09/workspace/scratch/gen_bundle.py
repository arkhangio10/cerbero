import json, sys

P = "/data/studio/projects/aurora"
B1 = "/data/studio/backups/aurora-2026-10-01"
B2 = "/data/studio/backups/aurora-2026-11-05"
U = "/data/studio/usb-archive/aurora"
POL = "POL-0004-0003 v2 (frozen digest c6e3...8219 in CERBERO-B-0004-01.md, evaluation EVL-0004-0002 with holdout cases, approved by the user)"


def bundle(bid, recs):
    out = [f"# CERBERO BUNDLE {bid}",
           f"- schema: {json.dumps('cerbero-memory-2')}",
           f"- bundle_id: {json.dumps(bid)}",
           f"- case_id: {json.dumps('CAS-0005')}",
           f"- scope_id: {json.dumps('SCP-0001')}",
           "- supersedes: null"]
    for rid, fields in recs:
        out.append("")
        out.append(f"## RECORD {rid}")
        for k, v in fields:
            out.append(f"- {k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(out) + "\n"


def chk(rid, doubt, decision, operation, outcomes, cost, budget):
    return (rid, [("type", "check-card"), ("doubt", doubt), ("decision", decision), ("operation", operation),
                  ("outcomes", outcomes), ("cost", cost), ("budget_left", budget)])


def obs(rid, card, agent, deleg, result, coverage):
    return (rid, [("type", "observation"), ("check_card", card), ("agent", agent), ("delegation", deleg),
                  ("state", "completed"), ("result", result), ("coverage", coverage),
                  ("observed_at", "unknown"), ("class", "observed")])


def st(rid, subject, state, located, statement, supports, depends):
    return (rid, [("type", "claim"), ("kind", "asset-state"), ("subject", subject), ("asset_state", state),
                  ("located_at", located), ("statement", statement), ("class", "observed"),
                  ("supports", supports), ("contradicts", []), ("depends_on", depends), ("status", "current")])


def contra(rid, cpy, statement, obsid, dep):
    return (rid, [("type", "claim"), ("kind", "contradiction"), ("subject", cpy), ("statement", statement),
                  ("class", "contradicted"), ("supports", [obsid]), ("contradicts", [cpy]),
                  ("depends_on", [cpy, obsid] + dep), ("status", "current")])


def cpy(rid, old, ver, path, sha, obs_):
    return (rid, [("type", "copy"), ("version_id", ver), ("real_path", path), ("location_id", "LOC-0001-0001"),
                  ("sha256", sha), ("observation", obs_), ("access", "readable"), ("status", "needs-review"),
                  ("supersedes", old)])


r1 = [
    ("CAS-0005", [("type", "case"), ("scope_id", "SCP-0001"),
                  ("request", "What-if: which files of project Aurora could be lost if the volume that holds the project failed"),
                  ("status", "open"), ("opened_in", "this session")]),
    ("STM-0005-0001", [("type", "statement"),
                       ("text", "I have nothing to add. Continue only with what you can verify, or stop."),
                       ("given_in", "this session, reply to the question on approved set and verification"),
                       ("class", "user-declared")]),
    obs("OBS-0005-0001", None, "file-agent", "D2",
        "6 folders exist and are readable, real path equal to the name given: " + P + ", /data/studio/cerbero-memory, " + B1 + ", " + B2 + ", " + U + ", /data/studio",
        "6 of 6 folders"),
    obs("OBS-0005-0002", None, "file-agent", "D3",
        "16 CERBERO- files in /data/studio/cerbero-memory, not truncated; newest index IDX-0004-01",
        "complete: 16 entries, limit 200, not truncated"),
    obs("OBS-0005-0003", None, "file-agent", "D7",
        "13 memory files hashed; the 12 bundles listed in IDX-0004-01 equal their index digests; CERBERO-IDX-0004-01.md is 7cea48dc1578c32066840d602cba182c5f6fe37820e975fa2902ab43cbd25296",
        "13 of 13 memory files, 77179 bytes"),
    chk("CHK-0005-0001",
        "Are the 12 recorded copies outside Volume 1 (CPY-0001-0012 to CPY-0001-0023) and the 3 raw/ originals present at their recorded paths, inside their roots, with the recorded size?",
        "which copies may be hashed and counted verified-now under a Volume 1 failure; raw/ digest review required by " + POL,
        "D5 file-agent, 15 paths",
        "present, inside its root, same size: hash next; absent, outside or other size: copy excluded, contradiction recorded",
        "metadata only, read-only", 300),
    obs("OBS-0005-0004", "CHK-0005-0001", "file-agent", "D5",
        "12 copies present, real path equal to the recorded path, size equal to the version; raw/DSC_0101.ARW 65536 bytes mtime 800 and raw/DSC_0150.ARW 65536 bytes mtime 802 present; raw/DSC_0142.ARW not_found",
        "15 of 15 paths"),
    chk("CHK-0005-0002",
        "Does " + B1 + " hold a copy of a version with no copy recorded outside Volume 1 (raw/ 65536 bytes, palette.ase 512, fonts-license.pdf 2048), and is its inventory still complete?",
        "whether those files are reported as lost under a Volume 1 failure",
        "D6 file-agent, of any size, depth 8, limit 200 (one listing instead of 3 size-filtered ones)",
        "file of 65536, 512 or 2048 bytes: candidate, hash next; none: no copy there; incomplete: split with D13",
        "one listing, read-only", 300),
    obs("OBS-0005-0005", "CHK-0005-0002", "file-agent", "D6",
        "5 files: brief.pdf 736, copy.docx 968, cover.tif 9396, layout.indd 16384, logo.ai 8192",
        "complete to depth 8: 5 entries, limit 200, not truncated, no unreadable subfolder"),
    chk("CHK-0005-0003",
        "Does " + B2 + " hold a copy of a version with no copy recorded outside Volume 1 (65536, 512 or 2048 bytes), and is its inventory still complete?",
        "whether those files are reported as lost under a Volume 1 failure",
        "D6 file-agent, of any size, depth 8, limit 200",
        "file of 65536, 512 or 2048 bytes: candidate, hash next; none: no copy there; incomplete: split with D13",
        "one listing, read-only", 300),
    obs("OBS-0005-0006", "CHK-0005-0003", "file-agent", "D6",
        "3 files: copy.docx 968, cover.tif 9396, layout.indd 16900 (no recorded version has 16900 bytes)",
        "complete to depth 8: 3 entries, limit 200, not truncated, no unreadable subfolder"),
    chk("CHK-0005-0004",
        "Does " + U + " hold a copy of a version with no copy recorded outside Volume 1 (65536, 512 or 2048 bytes), and is its inventory still complete?",
        "whether those files are reported as lost under a Volume 1 failure",
        "D6 file-agent, of any size, depth 8, limit 200",
        "file of 65536, 512 or 2048 bytes: candidate, hash next; none: no copy there; incomplete: split with D13",
        "one listing, read-only", 300),
    obs("OBS-0005-0007", "CHK-0005-0004", "file-agent", "D6",
        "5 files: brief.pdf 4096, copy.docx 6000, cover.tif 32768, layout.indd 15000, logo.ai 8192",
        "complete to depth 8: 5 entries, limit 200, not truncated, no unreadable subfolder"),
    chk("CHK-0005-0005",
        "Do the 12 recorded copies outside Volume 1 still hold their versions, and do raw/DSC_0101.ARW and raw/DSC_0150.ARW still hold VER-0001-0009 and VER-0001-0011?",
        "copies counted eligible verified-now under a Volume 1 failure; state of the raw/ originals under policy v2",
        "D7 file-agent, 14 files with expected digests from version records",
        "equal: eligible verified-now, or raw intact; different: copy excluded and contradiction, or raw altered",
        "14 digests, 243168 bytes, read-only", 300),
    obs("OBS-0005-0008", "CHK-0005-0005", "file-agent", "D7",
        "14 of 14 digests equal the expected version digest: CPY-0001-0012 to CPY-0001-0023 at their recorded paths, raw/DSC_0101.ARW equal VER-0001-0009, raw/DSC_0150.ARW equal VER-0001-0011",
        "14 files, 243168 bytes"),
    chk("CHK-0005-0006",
        "Which files are in " + P + " now that the map does not cover, and does any project file have a same-size file outside Volume 1?",
        "whether the list of files that could be lost is complete for the project folder; a size with no match in the three complete copy listings means no copy outside Volume 1",
        "D6 file-agent, of any size, depth 8, limit 200",
        "unrecorded file without size match outside Volume 1: at risk; with a match: hash next; incomplete: split with D13",
        "one listing, read-only", 286),
    obs("OBS-0005-0009", "CHK-0005-0006", "file-agent", "D6",
        "9 files: brief-FINAL.pdf 736, cover.tif 9396, exports/previews/cover-preview.jpg 4096, fonts-license.pdf 2048, logo.ai 8192, notes/README-RECOVERY.txt 237, palette.ase 512, raw/DSC_0101.ARW 65536, raw/DSC_0150.ARW 65536; brief.pdf, copy.docx, layout.indd and raw/DSC_0142.ARW absent",
        "complete to depth 8: 9 entries, limit 200, not truncated, no unreadable subfolder"),
    chk("CHK-0005-0007",
        "Do project files brief-FINAL.pdf, cover.tif and logo.ai, whose sizes match files outside Volume 1, hold VER-0001-0001, VER-0001-0003 and VER-0001-0007?",
        "whether their current content has a verified copy outside Volume 1 or exists only on Volume 1",
        "D7 file-agent, 3 files with expected digests from version records",
        "equal: covered by the copies counted; different: that content exists only on Volume 1",
        "3 digests, 18324 bytes, read-only", 286),
    obs("OBS-0005-0010", "CHK-0005-0007", "file-agent", "D7",
        "brief-FINAL.pdf 83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512 equal VER-0001-0001; cover.tif d85d08c3852b35a6fdbd2523446c8cf8c2c467c6f985f44890561760dbc75e59 differs from VER-0001-0003; logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda equal VER-0001-0007",
        "3 files, 18324 bytes"),
]

r2 = [
    st("CLM-0005-0001", "AST-0001-0009", "intact", None, "raw/DSC_0101.ARW is intact relative to VER-0001-0009", ["OBS-0005-0008"], ["VER-0001-0009", "OBS-0005-0008"]),
    st("CLM-0005-0002", "AST-0001-0011", "intact", None, "raw/DSC_0150.ARW is intact relative to VER-0001-0011", ["OBS-0005-0008"], ["VER-0001-0011", "OBS-0005-0008"]),
    st("CLM-0005-0003", "AST-0001-0010", "missing", None, "raw/DSC_0142.ARW is missing at its recorded path and absent from the complete project listing", ["OBS-0005-0004", "OBS-0005-0009"], ["VER-0001-0010", "OBS-0005-0004", "OBS-0005-0009"]),
    st("CLM-0005-0004", "AST-0001-0003", "altered", None, "cover.tif at its recorded path differs from VER-0001-0003", ["OBS-0005-0010"], ["VER-0001-0003", "OBS-0005-0010"]),
    st("CLM-0005-0005", "AST-0001-0001", "moved", P + "/brief-FINAL.pdf", "brief.pdf is absent at its recorded path; VER-0001-0001 is at brief-FINAL.pdf", ["OBS-0005-0009", "OBS-0005-0010"], ["VER-0001-0001", "OBS-0005-0009", "OBS-0005-0010"]),
    st("CLM-0005-0006", "AST-0001-0007", "intact", None, "logo.ai is intact relative to VER-0001-0007", ["OBS-0005-0010"], ["VER-0001-0007", "OBS-0005-0010"]),
    st("CLM-0005-0007", "AST-0001-0002", "missing", None, "copy.docx is absent from the complete project listing", ["OBS-0005-0009"], ["VER-0001-0002", "OBS-0005-0009"]),
    st("CLM-0005-0008", "AST-0001-0006", "missing", None, "layout.indd is absent from the complete project listing", ["OBS-0005-0009"], ["VER-0001-0006", "OBS-0005-0009"]),
    st("CLM-0005-0009", "AST-0001-0008", "intact-metadata", None, "palette.ase has its recorded size and time; not hashed", ["OBS-0005-0009"], ["VER-0001-0008", "OBS-0005-0009"]),
    st("CLM-0005-0010", "AST-0001-0005", "intact-metadata", None, "fonts-license.pdf has its recorded size and time; not hashed", ["OBS-0005-0009"], ["VER-0001-0005", "OBS-0005-0009"]),
    st("CLM-0005-0011", "AST-0001-0004", "intact-metadata", None, "cover-preview.jpg has its recorded size and time; not hashed; informational under " + POL, ["OBS-0005-0009"], ["VER-0001-0004", "OBS-0005-0009", "POL-0004-0003"]),
    contra("CLM-0005-0012", "CPY-0001-0001", "CPY-0001-0001 places VER-0001-0001 at " + P + "/brief.pdf; the complete project listing shows no file there", "OBS-0005-0009", []),
    contra("CLM-0005-0013", "CPY-0001-0002", "CPY-0001-0002 places VER-0001-0002 at " + P + "/copy.docx; the complete project listing shows no file there", "OBS-0005-0009", []),
    contra("CLM-0005-0014", "CPY-0001-0003", "CPY-0001-0003 records a9337b1d...3911 at " + P + "/cover.tif; D7 now returns d85d08c3...5e59", "OBS-0005-0010", []),
    contra("CLM-0005-0015", "CPY-0001-0006", "CPY-0001-0006 places VER-0001-0006 at " + P + "/layout.indd; the complete project listing shows no file there", "OBS-0005-0009", []),
    contra("CLM-0005-0016", "CPY-0001-0010", "CPY-0001-0010 places VER-0001-0010 at " + P + "/raw/DSC_0142.ARW; D5 returns not_found", "OBS-0005-0004", []),
    cpy("CPY-0005-0001", "CPY-0001-0001", "VER-0001-0001", P + "/brief.pdf", "83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512", "OBS-0001-0006"),
    cpy("CPY-0005-0002", "CPY-0001-0002", "VER-0001-0002", P + "/copy.docx", "8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495", "OBS-0001-0006"),
    cpy("CPY-0005-0003", "CPY-0001-0003", "VER-0001-0003", P + "/cover.tif", "a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911", "OBS-0001-0006"),
    cpy("CPY-0005-0004", "CPY-0001-0006", "VER-0001-0006", P + "/layout.indd", "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b", "OBS-0001-0006"),
    cpy("CPY-0005-0005", "CPY-0001-0010", "VER-0001-0010", P + "/raw/DSC_0142.ARW", "2653339b90e2c2b0bd1cb1abbf34d1bbabb08e3ece0c62710a8d4ea177f4fe1a", "OBS-0001-0006"),
    ("CLM-0005-0017", [("type", "claim"), ("kind", "recoverability"), ("subject", "LOC-0001-0002, LOC-0001-0003"),
                       ("statement", "Both backup folders are outside a Volume 1 failure: recorded on Volume 2 (DOM-0001-0002), a different volume of the same device DOM-0001-0003"),
                       ("class", "inferred"), ("supports", ["STM-0001-0003"]), ("contradicts", []),
                       ("depends_on", ["STM-0001-0003", "LOC-0001-0002", "LOC-0001-0003", "DOM-0001-0001", "DOM-0001-0002"]), ("status", "current")]),
    ("CLM-0005-0018", [("type", "claim"), ("kind", "recoverability"), ("subject", "LOC-0001-0004"),
                       ("statement", "The USB archive is outside a Volume 1 failure: recorded on device DOM-0001-0004, while Volume 1 is on device DOM-0001-0003; its volume is unknown"),
                       ("class", "inferred"), ("supports", ["STM-0001-0003"]), ("contradicts", []),
                       ("depends_on", ["STM-0001-0003", "LOC-0001-0004", "DOM-0001-0001", "DOM-0001-0003", "DOM-0001-0004"]), ("status", "current")]),
    ("MAP-0005-0001", [("type", "map"), ("subject", "SET-0001-0002"),
                       ("scenario", "domain failure of Volume 1 (DOM-0001-0001), the recorded volume of " + P),
                       ("verdict", "recoverable"),
                       ("members", {"AST-0001-0001": "VER-0001-0001: 1 eligible (CPY-0001-0012), 0 uncertain, verified-now",
                                    "AST-0001-0002": "VER-0001-0002: 2 eligible (CPY-0001-0013, CPY-0001-0017), 0 uncertain, verified-now",
                                    "AST-0001-0003": "VER-0001-0003: 2 eligible (CPY-0001-0014, CPY-0001-0018), 0 uncertain, verified-now",
                                    "AST-0001-0006": "VER-0001-0006: 1 eligible (CPY-0001-0015), 0 uncertain, verified-now",
                                    "AST-0001-0007": "VER-0001-0007: 2 eligible (CPY-0001-0016, CPY-0001-0023), 0 uncertain, verified-now"}),
                       ("evidence_level", "verified-now"),
                       ("unknowns", ["storage pool of every location", "the backup folders share device DOM-0001-0003 with Volume 1", "volume of the USB archive"])]),
    ("MAP-0005-0002", [("type", "map"), ("subject", "SET-0001-0001"),
                       ("scenario", "domain failure of Volume 1 (DOM-0001-0001), the recorded volume of " + P),
                       ("verdict", "recoverable"),
                       ("members", {"AST-0001-0001": "VER-0001-0012: 1 eligible (CPY-0001-0019), 0 uncertain, verified-now",
                                    "AST-0001-0006": "VER-0001-0013: 1 eligible (CPY-0001-0022), 0 uncertain, verified-now",
                                    "AST-0001-0002": "VER-0001-0014: 1 eligible (CPY-0001-0020), 0 uncertain, verified-now",
                                    "AST-0001-0003": "VER-0001-0015: 1 eligible (CPY-0001-0021), 0 uncertain, verified-now",
                                    "AST-0001-0007": "VER-0001-0007: 2 eligible (CPY-0001-0016, CPY-0001-0023), 0 uncertain, verified-now"}),
                       ("evidence_level", "verified-now"),
                       ("unknowns", ["volume of the USB archive", "independence of the USB archive rests on the device statement STM-0001-0003 only"])]),
    ("MAP-0005-0003", [("type", "map"), ("subject", "SCP-0001"),
                       ("scenario", "domain failure of Volume 1 (DOM-0001-0001); recorded files outside the approved sets; raw/ reviewed as critical because of " + POL),
                       ("verdict", "not-recoverable"),
                       ("members", {"AST-0001-0009": "VER-0001-0009 (critical by policy): 0 eligible, 0 uncertain, none; only copy is the project file",
                                    "AST-0001-0011": "VER-0001-0011 (critical by policy): 0 eligible, 0 uncertain, none; only copy is the project file",
                                    "AST-0001-0010": "VER-0001-0010 (critical by policy): 0 eligible, 0 uncertain, none; already missing",
                                    "AST-0001-0008": "VER-0001-0008: 0 eligible, 0 uncertain, none",
                                    "AST-0001-0005": "VER-0001-0005: 0 eligible, 0 uncertain, none",
                                    "AST-0001-0004": "VER-0001-0004: 0 eligible, 0 uncertain, none; informational by policy, not reported as at risk"}),
                       ("evidence_level", "none"),
                       ("unknowns", [])]),
    ("OPN-0005-0001", [("type", "open-item"), ("subject", "LOC-0001-0001, LOC-0001-0002, LOC-0001-0003, LOC-0001-0004"),
                       ("reason", "storage pool unknown for every location; a pool or NAS device failure would reach both volumes and was not evaluated"),
                       ("needed_to_resolve", "a user statement of the storage pool of Volume 1 and Volume 2")]),
    ("OPN-0005-0002", [("type", "open-item"), ("subject", "AST-0001-0003"),
                       ("reason", "current project cover.tif (d85d08c3...5e59) differs from VER-0001-0003; that content has no copy outside Volume 1; cause unknown"),
                       ("needed_to_resolve", "a user statement whether the change is legitimate")]),
    ("OPN-0005-0003", [("type", "open-item"), ("subject", P + "/notes/README-RECOVERY.txt"),
                       ("reason", "not a recorded asset; 237 bytes, no file of that size outside Volume 1; holds instruction-like text FND-0002-0001 and FND-0002-0002, not acted on"),
                       ("needed_to_resolve", "a Baseline that records it, if the user wants it kept")]),
    ("OPN-0005-0004", [("type", "open-item"), ("subject", "LOC-0001-0004"),
                       ("reason", "volume layout of the USB archive unknown (STM-0001-0003); the NAS shows it under /data/studio"),
                       ("needed_to_resolve", "a user statement of the volume or device of the USB archive")]),
]

which = sys.argv[1]
if which == "1":
    sys.stdout.buffer.write(bundle("B-0005-01", r1).encode("utf-8"))
else:
    sys.stdout.buffer.write(bundle("B-0005-02", r2).encode("utf-8"))
