from gen_bundle import render, write_save, SQ
import plan_records as P

recs = list(P.recs)


def R(rid, typ, *pairs):
    recs.append((rid, [("type", typ)] + list(pairs)))


R("OBS-0002-0010", "observation", ("check_card", None), ("agent", "knowledge-agent"), ("delegation", "D10"), ("state", "completed"),
  ("result", "save of plan bundle B-0002-01 (file name hint CERBERO-B-0002-01): NAS approval APV-1 granted by the user; result saved_file /data/studio/cerbero-memory/CERBERO-B-0002-01.md, verified false, saved_bytes 20200"),
  ("coverage", "1 save"), ("observed_at", "unknown"), ("class", "observed"))
R("OPN-0002-0003", "open-item", ("subject", "/data/studio/cerbero-memory/CERBERO-B-0002-01.md"),
  ("reason", "the save of plan bundle B-0002-01 returned verified false, so the plan is not persisted; the file is not used as evidence and is listed as needs-review, without a digest"),
  ("needed_to_resolve", "a new plan revision saved with a verified result, hashed with D7 and confirmed by the user"))
R("APR-0002-0001", "approval", ("plan_id", "PLN-0002-01"), ("plan_sha256", None), ("decision", "not-requested"),
  ("statement", "the plan confirmation was never asked: the mandatory plan save returned verified false (OBS-0002-0010); the user granted only the NAS approval APV-1 of the save itself"))
R("RCP-0002-01", "receipt", ("plan_id", "PLN-0002-01"), ("plan_sha256", None), ("overall", "failed"), ("reference", "approved-version"), ("set_complete", False),
  ("coverage", "4 of 5 Delivery 2 members intact by digest in the project; layout.indd missing; recorded copy CPY-0001-0015 verified-now; no folder created, nothing copied"),
  ("pending", ["ENT-0002-01-01 layout.indd (VER-0001-0006): not-attempted"]),
  ("reason", "mandatory plan save not persisted: D10 returned verified false for /data/studio/cerbero-memory/CERBERO-B-0002-01.md (20200 bytes); per the recovery protocol no folder is created and nothing is copied"))
R("REN-0002-01-01", "receipt-entry", ("receipt_id", "RCP-0002-01"), ("entry_id", "ENT-0002-01-01"), ("asset_id", "AST-0001-0006"), ("version_id", "VER-0001-0006"),
  ("status", "not-attempted"), ("destination_path", None), ("source_sha256_before", None), ("destination_sha256", None), ("source_sha256_after", None),
  ("note", "not executed because the plan was not persisted; during source selection the source /data/studio/backups/aurora-2026-10-01/layout.indd had digest 84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b (OBS-0002-0009), equal to VER-0001-0006; /data/studio/recovered/cerbero-recovery-CAS-0002 was not created"))

text = render("B-0002-02", "CAS-0002", "SCP-0001", recs)
with open("bundle_B-0002-02.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
write_save("B-0002-02", text, "d10_B-0002-02.sh")
print(len(text.encode("utf-8")), "bytes;", len(recs), "records; single quotes:", text.count(SQ))
