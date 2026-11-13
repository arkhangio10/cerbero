import sys; sys.path.insert(0,'scratch')
from bundle import bundle
V={'0001':'83ba1a47e756a9d9b5642c173f1db1204a4bd6fe1fce1877e8914ad432339512','0002':'8abd843fb54d553068df3a71c5f4bd85a24207ee55730aaae2f2626724ca3495','0003':'a9337b1da249a4f4815a2282959b6f5ce517903a89e4314d3ae819dd863c3911','0006':'84a443e4aef7b06d2bab8f71152d3964a73d2ee51b0bbe10cdfeff731cab1e1b','0007':'1dbd46163c5360d54c5df100c27933b7ebd5741fa06deb62ec3d06defe840eda'}
PLAN='be0c66eea965a7f9c967b2d7b075c118e40a0cf355181c7d88a6b8094a468475'
P='/data/studio/projects/aurora/'; B='/data/studio/backups/aurora-2026-10-01/'; R='/data/studio/recovered/cerbero-rebuild-CAS-0003/'
WORDS="Yes. I confirm the approved set you showed and I approve plan PLN-0003-01 with that digest."
def obs(i,dlg,agent,res,cov):
    return (f"OBS-0003-{i:04d}",[("type","observation"),("check_card",None),("agent",agent),("delegation",dlg),("state","completed"),("result",res),("coverage",cov),("observed_at","unknown"),("class","observed")])
recs=[]
recs.append(("STM-0003-0002",[("type","statement"),("text",WORDS),("given_in","this session"),("class","user-declared")]))
recs.append(("APR-0003-01",[("type","approval"),("plan_id","PLN-0003-01"),("plan_sha256",PLAN),("decision","granted"),("statement",WORDS)]))
recs.append(obs(15,"D10, D10, D7","knowledge-agent, file-agent","B-0003-01 saved at /data/studio/cerbero-memory/CERBERO-B-0003-01.md, verified, 14160 bytes, sha256 50001a3c50a8bfbdb8ccc89acec203315e516a8b88bbbf0a0a7c8eb4c24e4e7a; B-0003-02 saved at /data/studio/cerbero-memory/CERBERO-B-0003-02.md, verified, 8287 bytes, sha256 "+PLAN+"; NAS approvals APV-1 and APV-2 granted by the user","2 of 2 saves persisted"))
recs.append(obs(16,"D7","file-agent","plan file /data/studio/cerbero-memory/CERBERO-B-0003-02.md re-hashed before the first change: "+PLAN+", match","1 of 1"))
recs.append(obs(17,"D11","file-agent","created /data/studio/recovered/cerbero-rebuild-CAS-0003, equal to the planned path; NAS approval APV-3 granted by the user","1 of 1 folder"))
ents=[("01","AST-0001-0001","brief.pdf","VER-0001-0001",V['0001'],P+"brief-FINAL.pdf","APV-4","original in the project, moved to brief-FINAL.pdf"),
      ("02","AST-0001-0006","layout.indd","VER-0001-0006",V['0006'],B+"layout.indd","APV-5","copy in backups/aurora-2026-10-01"),
      ("03","AST-0001-0002","copy.docx","VER-0001-0002",V['0002'],B+"copy.docx","APV-6","copy in backups/aurora-2026-10-01"),
      ("04","AST-0001-0003","cover.tif","VER-0001-0003",V['0003'],B+"cover.tif","APV-7","copy in backups/aurora-2026-10-01 (project file altered)"),
      ("05","AST-0001-0007","logo.ai","VER-0001-0007",V['0007'],P+"logo.ai","APV-8","original in the project, intact")]
fmt={"brief.pdf":"opened by document-agent, whole file read (OBS-0003-0023)","copy.docx":"opened by document-agent, whole file read (OBS-0003-0024)"}
for i,(e,a,n,v,d,src,apv,prov) in enumerate(ents):
    recs.append(obs(18+i,"D5, D7, D12, D7","file-agent",f"ENT-0003-01-{e}: destination {R+n} absent before copy; source {src} digest {d} equal to expected; copied, real destination path equal to planned; destination digest {d} equal to expected; NAS approval {apv} granted by the user","1 of 1 entry"))
recs.append(obs(23,"D8","document-agent","rebuilt brief.pdf opened; first lines quoted: AURORA brief v2 - Delivery 2 / Synthetic demo document, approved version. / No real client data.; no instruction-like passage","whole file read"))
recs.append(obs(24,"D8","document-agent","rebuilt copy.docx opened; first lines quoted: AURORA copy v2 - Delivery 2 / Synthetic approved copy text for the demo.; no instruction-like passage","whole file read"))
recs.append(("RCP-0003-01",[("type","receipt"),("plan_id","PLN-0003-01"),("plan_sha256",PLAN),("overall","verified"),("reference","approved-version"),("set_complete",True),
 ("coverage","5 of 5 target members planned, copied and verified by digest against approved versions; format check: 2 documents opened whole by document-agent, 3 files (layout.indd, cover.tif, logo.ai) format check not available"),
 ("pending",[]),("reason",None),("outside_target",["AST-0001-0010"])]))
for i,(e,a,n,v,d,src,apv,prov) in enumerate(ents):
    recs.append((f"REN-0003-01-{e}",[("type","receipt-entry"),("receipt_id","RCP-0003-01"),("entry_id",f"ENT-0003-01-{e}"),("asset_id",a),("version_id",v),("status","verified"),("destination_path",R+n),
     ("source_sha256_before",d),("destination_sha256",d),("source_sha256_after",None),("note",f"evidence OBS-0003-{18+i:04d}"),("name",n),("source_path",src),
     ("checks",{"bytes":"equal to the source digest observed before copying","version":f"equal to approved version {v}","format":fmt.get(n,"format check not available"),"provenance":prov})]))
txt=bundle("B-0003-03","CAS-0003","SCP-0001",recs)
open('scratch/B-0003-03.md','w',encoding='utf-8',newline='\n').write(txt)
print(len(txt.encode('utf-8')), "bytes; single quotes:", txt.count(chr(39)))
