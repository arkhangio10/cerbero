BUNDLE_ID = "B-0002-02"
CASE_ID = "CAS-0002"
SCOPE_ID = "SCP-0001"
HINT = "CERBERO-B-0002-02"
OUT_MD = "receipt_bundle.md"
OUT_SH = "d10_receipt.sh"

V6 = "84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b"
PD = "bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569"
RF = "/data/studio/recovered/cerbero-recovery-CAS-0002"
RECS = []


def R(rid, **f):
    RECS.append((rid, f))


def O(rid, agent, dlg, result, coverage):
    R(rid, type="observation", check_card=None, agent=agent, delegation=dlg, state="completed", result=result, coverage=coverage, observed_at="unknown", class_="observed")


O("OBS-0002-0013", "knowledge-agent", "D10", "plan bundle B-0002-01 saved at /data/studio/cerbero-memory/CERBERO-B-0002-01.md, verified true, 20258 bytes; NAS approval APV-1 answered by the user: granted", "1 of 1 saves")
O("OBS-0002-0014", "file-agent", "D7", "/data/studio/cerbero-memory/CERBERO-B-0002-01.md sha256 " + PD + ", 20258 bytes", "1 of 1 files hashed")
O("OBS-0002-0015", "file-agent", "D7", "plan file re-hashed immediately before the first change: sha256 " + PD + ", matches the confirmed digest", "1 of 1 files hashed")
O("OBS-0002-0016", "file-agent", "D11", "created " + RF + " (no subfolders); NAS approval APV-2 answered by the user: granted", "1 of 1 folders")
O("OBS-0002-0017", "file-agent", "D5", RF + "/layout.indd does not exist (reason not_found)", "1 of 1 paths")
O("OBS-0002-0018", "file-agent", "D7", "source /data/studio/backups/aurora-2026-10-01/layout.indd sha256 " + V6 + ", 16384 bytes, matches expected, immediately before copying", "1 of 1 files hashed")
O("OBS-0002-0019", "file-agent", "D12", "copied /data/studio/backups/aurora-2026-10-01/layout.indd; real destination path " + RF + "/layout.indd; NAS result copied; NAS approval APV-3 answered by the user: granted", "1 of 1 copies")
O("OBS-0002-0020", "file-agent", "D7", "destination " + RF + "/layout.indd sha256 " + V6 + ", 16384 bytes, matches expected", "1 of 1 files hashed")

R("APR-0002-01", type="approval", plan_id="PLN-0002-01", plan_sha256=PD, decision="granted",
  statement="Yes. I confirm the approved set you showed and I approve plan PLN-0002-01 with that digest.")

R("RCP-0002-01", type="receipt", plan_id="PLN-0002-01", plan_sha256=PD, overall="partial", reference="approved-version", set_complete=False,
  coverage="1 plan entry executed and verified by digest at its destination; source checked before the copy; copy.docx, cover.tif and logo.ai intact by digest at their recorded paths (CLM-0002-0002, CLM-0002-0003, CLM-0002-0004); brief.pdf not checked (recorded path not canonical); 6 ordinary assets checked by metadata only; 5 listings complete to depth 8 (1 memory listing, 4 size-filtered searches); 9 digests computed in this session before this receipt",
  pending=["AST-0001-0001 brief.pdf (VER-0001-0001): out of scope, state unknown, not recovered (OPN-0002-0001)"],
  reason="Entry ENT-0002-01-01 (layout.indd, VER-0001-0006) verified. Delivery 2 member brief.pdf stays pending because its recorded path is not canonical and was not read, so the target set SET-0001-0002 is not shown complete.")
R("REN-0002-01-01", type="receipt-entry", receipt_id="RCP-0002-01", entry_id="ENT-0002-01-01", asset_id="AST-0001-0006", version_id="VER-0001-0006", status="verified",
  destination_path=RF + "/layout.indd", source_sha256_before=V6, destination_sha256=V6, source_sha256_after=None,
  note="source re-hashed before the copy (OBS-0002-0018); destination digest equals VER-0001-0006 (OBS-0002-0020); source not re-hashed after because the destination matched")
R("REN-0002-01-02", type="receipt-entry", receipt_id="RCP-0002-01", entry_id=None, asset_id="AST-0001-0001", version_id="VER-0001-0001", status="out-of-scope",
  destination_path=None, source_sha256_before=None, destination_sha256=None, source_sha256_after=None,
  note="recorded path /data/studio/projects/aurora/../../private/other-client/brief.pdf is not canonical; listed as pending in PLN-0002-01 and not executed")
