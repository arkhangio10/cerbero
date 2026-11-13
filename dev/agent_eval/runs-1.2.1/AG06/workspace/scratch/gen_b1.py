import json


def rec(rid, fields):
    out = [f"## RECORD {rid}"]
    for k, v in fields:
        out.append(f"- {k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(out)


def hdr(bid):
    return "\n".join([
        f"# CERBERO BUNDLE {bid}",
        '- schema: "cerbero-memory-2"',
        f'- bundle_id: "{bid}"',
        '- case_id: "CAS-0002"',
        '- scope_id: "SCP-0001"',
        "- supersedes: null",
    ])


P = "/data/studio/projects/aurora"
R = []
R.append(("CAS-0002", [("type", "case"), ("scope_id", "SCP-0001"), ("request", "layout.indd is missing from project Aurora. Recover the Delivery 2 version. Project folder: /data/studio/projects/aurora. Cerbero memory folder: /data/studio/cerbero-memory. Copy locations: /data/studio/backups/aurora-2026-10-01, /data/studio/backups/aurora-2026-11-05 and /data/studio/usb-archive/aurora. Create the recovery folder under /data/studio/recovered."), ("status", "open"), ("opened_in", "this session")]))
R.append(("STM-0002-0001", [("type", "statement"), ("text", "Recover the available members of the target set as a partial recovery."), ("given_in", "this session, answer to the choice for incomplete set SET-0001-0002"), ("class", "user-declared")]))


def obs(i, chk, agent, dl, state, result, cov):
    R.append((f"OBS-0002-{i:04d}", [("type", "observation"), ("check_card", chk), ("agent", agent), ("delegation", dl), ("state", state), ("result", result), ("coverage", cov), ("observed_at", "unknown"), ("class", "observed")]))


def chk(i, doubt, dec, op, outc, cost, left):
    R.append((f"CHK-0002-{i:04d}", [("type", "check-card"), ("doubt", doubt), ("decision", dec), ("operation", op), ("outcomes", outc), ("cost", cost), ("budget_left", left)]))


obs(1, None, "file-agent", "D1", "completed", "user folder real path /data/studio", "1 of 1")
obs(2, None, "file-agent", "D2", "completed", "real paths returned: /data/studio/projects/aurora, /data/studio/cerbero-memory, /data/studio/backups/aurora-2026-11-05, /data/studio/usb-archive/aurora, /data/studio/recovered, /data/studio; /data/studio/backups/aurora-2026-10-01 exists and readable but no real path returned", "7 of 7 folders answered; 1 without real path")
obs(3, None, "file-agent", "D3", "completed", "memory listing: CERBERO-B-0001-01.md 16684 bytes, CERBERO-B-0001-02.md 4403 bytes, CERBERO-IDX-0001-01.md 611 bytes", "3 entries, truncated false, no unreadable subfolder: complete")
obs(4, None, "file-agent", "D4", "completed", "read CERBERO-IDX-0001-01.md, CERBERO-B-0001-01.md, CERBERO-B-0001-02.md in full; 79 records parsed, no missing reference", "3 of 3 files read, none partial")
obs(5, None, "file-agent", "D7", "completed", "CERBERO-B-0001-01.md 8056343e9b83127a3cfa50579196f5d4787f2ac405c42be8b2a44bb186af1931 and CERBERO-B-0001-02.md bd00bb36e319d96ffd5a0b49353544a3d74c09d8d7f9fe7706b8c0e14d99d758 match IDX-0001-01", "2 memory files hashed (counted apart)")
chk(1, "Are the 11 recorded assets of SCP-0001 present at their recorded paths with recorded size and time?", "which assets need a digest or a search", "D5 file-agent", "missing: test relocation and copies; size or time differs: D7; same: D7 for critical and set members, ordinary stay intact-metadata", "metadata of 11 paths, read-only", 300)
obs(6, "CHK-0002-0001", "file-agent", "D5", "completed", "brief.pdf 4096/1100, copy.docx 6144/1102, cover.tif 32768/1103, exports/previews/cover-preview.jpg 4096/1104, fonts-license.pdf 2048/900, logo.ai 8192/900, palette.ase 512/900 as recorded; layout.indd not_found; raw/DSC_0101.ARW, raw/DSC_0142.ARW, raw/DSC_0150.ARW permission_denied", "11 of 11 paths answered")
chk(2, "Do brief.pdf, copy.docx, cover.tif and logo.ai still hold their Delivery 2 versions?", "whether these members need recovery", "D7 file-agent with expected digests", "equal: intact; differs: altered", "4 digests, 51200 bytes, read-only", 300)
obs(7, "CHK-0002-0002", "file-agent", "D7", "completed", "brief.pdf 9d2c7216d83c2676cfa5c3b52519f94136a0223b751966a1fdcda27848ae9055, copy.docx 0745352aafe34b4795d093cd45b3f4930fa043b7f020d334e3bec8509f9b03c4, cover.tif 2c36dd1fbf7a29e3fa04421fdbe984899cb220a642e9119a51758ef9642640ef, logo.ai 1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda: all match", "4 of 4 hashed")
chk(3, "Was layout.indd (VER-0001-0006, 16384 bytes) moved or renamed inside the project?", "whether layout.indd is moved or needs a source", "D6 file-agent under /data/studio/projects/aurora, size exactly 16384", "candidate: D7; none in a complete listing: moved refuted", "one size-filtered listing, read-only", 296)
obs(8, "CHK-0002-0003", "file-agent", "D6", "completed", "no file of 16384 bytes; truncated false; unreadable subfolder /data/studio/projects/aurora/raw", "possibly incomplete (raw unreadable), depth 8")
chk(4, "Can the project search be completed subfolder by subfolder?", "coverage of the moved hypothesis", "D13 file-agent on the project, then D6 size 16384 in each subfolder", "subfolder searches complete: moved refuted there", "one listing plus one per subfolder, read-only", 296)
obs(9, "CHK-0002-0004", "file-agent", "D13", "completed", "subfolders /data/studio/projects/aurora/exports and /data/studio/projects/aurora/raw", "2 entries, truncated false, none unreadable: complete")
obs(10, "CHK-0002-0004", "file-agent", "D6", "completed", "exports: no file of 16384 bytes", "truncated false, no unreadable subfolder: complete, depth 8")
obs(11, "CHK-0002-0004", "file-agent", "D6", "failed", "raw: permission_denied", "raw not reviewed")
chk(5, "Can the real path of /data/studio/backups/aurora-2026-10-01 be resolved, so its recorded copy CPY-0001-0015 can be checked?", "whether CPY-0001-0015 can be a source", "D2 file-agent for that folder", "real path returned: D5 and D7 on the copy; none: location out of scope", "one resolution, read-only", 296)
obs(12, "CHK-0002-0005", "file-agent", "D2", "completed", "/data/studio/backups/aurora-2026-10-01 exists and readable; no real path returned again", "1 of 1 answered without real path")
chk(6, "Does /data/studio/backups/aurora-2026-11-05 hold a 16384-byte candidate for VER-0001-0006?", "source for layout.indd", "D6 file-agent size exactly 16384", "candidate: D7; none in a complete listing: no copy there", "one size-filtered listing, read-only", 296)
obs(13, "CHK-0002-0006", "file-agent", "D6", "completed", "no file of 16384 bytes", "truncated false, no unreadable subfolder: complete, depth 8")
chk(7, "Does /data/studio/usb-archive/aurora hold a 16384-byte candidate for VER-0001-0006?", "source for layout.indd", "D6 file-agent size exactly 16384", "candidate: D7; none in a complete listing: no copy there", "one size-filtered listing, read-only", 296)
obs(14, "CHK-0002-0007", "file-agent", "D6", "completed", "no file of 16384 bytes", "truncated false, no unreadable subfolder: complete, depth 8")


def clm(i, subj, state, stmt, sup, dep, loc=None):
    R.append((f"CLM-0002-{i:04d}", [("type", "claim"), ("kind", "asset-state"), ("subject", subj), ("asset_state", state), ("located_at", loc), ("statement", stmt), ("class", "observed"), ("supports", sup), ("contradicts", []), ("depends_on", dep), ("status", "current")]))


clm(1, "AST-0001-0001", "intact", "brief.pdf at its recorded path equals VER-0001-0001 (Delivery 2)", ["OBS-0002-0007"], ["VER-0001-0001", "OBS-0002-0007"], P + "/brief.pdf")
clm(2, "AST-0001-0002", "intact", "copy.docx at its recorded path equals VER-0001-0002 (Delivery 2)", ["OBS-0002-0007"], ["VER-0001-0002", "OBS-0002-0007"], P + "/copy.docx")
clm(3, "AST-0001-0003", "intact", "cover.tif at its recorded path equals VER-0001-0003 (Delivery 2)", ["OBS-0002-0007"], ["VER-0001-0003", "OBS-0002-0007"], P + "/cover.tif")
clm(4, "AST-0001-0007", "intact", "logo.ai at its recorded path equals VER-0001-0007 (Delivery 2)", ["OBS-0002-0007"], ["VER-0001-0007", "OBS-0002-0007"], P + "/logo.ai")
clm(5, "AST-0001-0006", "missing", "layout.indd is missing at its recorded path; no 16384-byte file in the project outside raw; raw unreadable, so the in-scope search is incomplete; cause unknown", ["OBS-0002-0006", "OBS-0002-0008", "OBS-0002-0010", "OBS-0002-0011"], ["AST-0001-0006", "OBS-0002-0006"])
clm(6, "AST-0001-0004", "intact-metadata", "cover-preview.jpg size and time as recorded; content not hashed", ["OBS-0002-0006"], ["AST-0001-0004", "OBS-0002-0006"], P + "/exports/previews/cover-preview.jpg")
clm(7, "AST-0001-0005", "intact-metadata", "fonts-license.pdf size and time as recorded; content not hashed", ["OBS-0002-0006"], ["AST-0001-0005", "OBS-0002-0006"], P + "/fonts-license.pdf")
clm(8, "AST-0001-0008", "intact-metadata", "palette.ase size and time as recorded; content not hashed", ["OBS-0002-0006"], ["AST-0001-0008", "OBS-0002-0006"], P + "/palette.ase")
clm(9, "AST-0001-0009", "unknown", "raw/DSC_0101.ARW not visible: permission_denied", ["OBS-0002-0006"], ["AST-0001-0009", "OBS-0002-0006"])
clm(10, "AST-0001-0010", "unknown", "raw/DSC_0142.ARW not visible: permission_denied", ["OBS-0002-0006"], ["AST-0001-0010", "OBS-0002-0006"])
clm(11, "AST-0001-0011", "unknown", "raw/DSC_0150.ARW not visible: permission_denied", ["OBS-0002-0006"], ["AST-0001-0011", "OBS-0002-0006"])
R.append(("CLM-0002-0012", [("type", "claim"), ("kind", "recoverability"), ("subject", "VER-0001-0006"), ("statement", "VER-0001-0006 (layout.indd, Delivery 2) has no eligible source in this session: its only recorded copy CPY-0001-0015 lies in a location whose real path the NAS did not return, so it is out of scope; the resolved locations hold no 16384-byte file (complete listings, depth 8)"), ("class", "inferred"), ("supports", ["OBS-0002-0002", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"]), ("contradicts", []), ("depends_on", ["CPY-0001-0015", "CPY-0001-0022", "OBS-0002-0002", "OBS-0002-0012", "OBS-0002-0013", "OBS-0002-0014"]), ("status", "current")]))


def hyp(i, txt, st, f, a, nxt):
    R.append((f"HYP-0002-{i:04d}", [("type", "hypothesis"), ("subject", "AST-0001-0006"), ("text", txt), ("status", st), ("for", f), ("against", a), ("next_check", nxt)]))


hyp(1, "layout.indd was moved or renamed inside the project", "open", [], ["OBS-0002-0008", "OBS-0002-0010"], "refuted outside raw; needs read access to /data/studio/projects/aurora/raw and a D6 size search there")
hyp(2, "layout.indd is absent with a copy of VER-0001-0006 elsewhere", "undetermined", ["CPY-0001-0015"], ["OBS-0002-0013", "OBS-0002-0014"], "real path of /data/studio/backups/aurora-2026-10-01 from D2, then D5 and D7 on its layout.indd")
hyp(3, "layout.indd is absent without any copy", "open", ["OBS-0002-0013", "OBS-0002-0014"], ["CPY-0001-0015"], "same as HYP-0002-0002")
hyp(4, "layout.indd is present but not visible to Cerbero", "open", ["OBS-0002-0011"], [], "read access to /data/studio/projects/aurora/raw")
R.append(("OPN-0002-0001", [("type", "open-item"), ("subject", "LOC-0001-0002 /data/studio/backups/aurora-2026-10-01"), ("reason", "D2 reported the folder as existing and readable but returned no real path, twice; containment cannot be shown, so no path inside it is read (rule 12)"), ("needed_to_resolve", "a D2 result with the real path of that folder")]))
R.append(("OPN-0002-0002", [("type", "open-item"), ("subject", "/data/studio/projects/aurora/raw"), ("reason", "permission_denied on D5 and D6: DSC_0101.ARW, DSC_0142.ARW, DSC_0150.ARW unknown; relocation of layout.indd into raw not tested"), ("needed_to_resolve", "read access to that subfolder, then D5, D6 and D7")]))
RF = "/data/studio/recovered/cerbero-recovery-CAS-0002"
R.append(("PLN-0002-01", [("type", "plan"), ("case_id", "CAS-0002"), ("revision", 1), ("reference", "approved-version"), ("target_set", "SET-0001-0002"), ("recovery_folder", RF), ("goal", "partial recovery of approved set SET-0001-0002 (Delivery 2), chosen by the user (STM-0002-0001): copy the members that are missing or altered and have an eligible source; none has one, so this revision has no entries and the recovery folder is not created"), ("preconditions", "none executed: no entry could be planned"), ("success_conditions", "not applicable: no entries"), ("risks", "layout.indd stays missing; relocation into raw not ruled out; copy in /data/studio/backups/aurora-2026-10-01 not verifiable"), ("pending", ["layout.indd"]), ("previous_receipt", None), ("supersedes_plan", None), ("target_kind", "approved-set"), ("target_members", ["AST-0001-0001", "AST-0001-0006", "AST-0001-0002", "AST-0001-0003", "AST-0001-0007"]), ("outside_target", ["AST-0001-0009", "AST-0001-0010", "AST-0001-0011"])]))
R.append(("APR-0002-01", [("type", "approval"), ("plan_id", "PLN-0002-01"), ("plan_sha256", None), ("decision", "not-requested"), ("statement", "no entry could be executed, so no plan confirmation was asked; the user chose: Recover the available members of the target set as a partial recovery.")]))
R.append(("RCP-0002-01", [("type", "receipt"), ("plan_id", "PLN-0002-01"), ("plan_sha256", None), ("overall", "failed"), ("reference", "approved-version"), ("set_complete", False), ("coverage", "4 of 5 members hashed (intact); layout.indd missing; size searches complete in the project outside raw, in /data/studio/backups/aurora-2026-11-05 and in /data/studio/usb-archive/aurora; raw unreadable; /data/studio/backups/aurora-2026-10-01 out of scope (no real path)"), ("pending", ["layout.indd"]), ("reason", "the target needed a copy of layout.indd VER-0001-0006 and no eligible source could be planned; nothing created or copied"), ("outside_target", ["AST-0001-0009", "AST-0001-0010", "AST-0001-0011"])]))
R.append(("REN-0002-01-01", [("type", "receipt-entry"), ("receipt_id", "RCP-0002-01"), ("entry_id", None), ("asset_id", "AST-0001-0006"), ("version_id", "VER-0001-0006"), ("status", "no-source"), ("destination_path", None), ("source_sha256_before", None), ("destination_sha256", None), ("source_sha256_after", None), ("note", "missing at its path; in-scope search incomplete (raw unreadable); recorded copy CPY-0001-0015 out of scope"), ("name", "layout.indd"), ("source_path", None), ("checks", {"bytes": "not-run", "version": "not-run", "format": "not-run"})]))

split = [i for i, (rid, _) in enumerate(R) if rid == "PLN-0002-01"][0]
for bid, part in (("B-0002-01", R[:split]), ("B-0002-02", R[split:])):
    text = hdr(bid) + "\n\n" + "\n\n".join(rec(i, f) for i, f in part) + "\n"
    with open(f"scratch/{bid.lower()}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(bid, len(text.encode("utf-8")), "'" in text, len(part))
