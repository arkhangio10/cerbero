import sys; sys.path.insert(0,'scratch')
from bundle import bundle
M='/data/studio/cerbero-memory/'
rows=[("B-0001-01","dc616afa8ebc5a303d71bbaff7420d19c8ed646b512a29bf7c635962889bd85b","current"),
      ("B-0001-02","6cde1fb8957f6539a2c7d346f0280df34cad4d3d8467d4555352bc0c377e2a1e","current"),
      ("IDX-0001-01","ee227cf5abcf13f4d4e8a7ab1a1b849f4cd54c5023068e260e36703e0eaf93a6","superseded"),
      ("B-0002-01","de48e7098e5890f79d442ca39128296e30b026231e83be54bc080ab87ca27edf","current"),
      ("B-0002-02","6e49138c3ebde1506a6b49ed5e7a9d6c323727514dbc7801dcaeee40a721e121","current"),
      ("B-0002-03","d55e0770e8b14aea2f4b510d3982dac4ae4db134fe7aa3233e6f088ae8086ccf","current"),
      ("IDX-0002-01","43bed17b4676e0165d7e51674d96e4e0aeb77b49d6aa57d2b5b5922efc9f594a","superseded"),
      ("B-0003-01","50001a3c50a8bfbdb8ccc89acec203315e516a8b88bbbf0a0a7c8eb4c24e4e7a","current"),
      ("B-0003-02","be0c66eea965a7f9c967b2d7b075c118e40a0cf355181c7d88a6b8094a468475","current"),
      ("B-0003-03","d82107efb138469a257a835b2e57488c11d4b10944b019a88216640fe59c8603","current")]
recs=[(f"IDX-0003-01-{i+1:04d}",[("type","index-entry"),("file",f"{M}CERBERO-{b}.md"),("bundle_id",b),("sha256",d),("status",s)]) for i,(b,d,s) in enumerate(rows)]
txt=bundle("IDX-0003-01","CAS-0003","SCP-0001",recs)
open('scratch/IDX-0003-01.md','w',encoding='utf-8',newline='\n').write(txt)
ins="Save the Markdown text below as a new text file in the folder /data/studio/cerbero-memory, using the file name hint CERBERO-IDX-0003-01. Never replace or append to an existing file; if that name is taken, stop and report it. Return the saved file path exactly as the NAS reports it, whether the save was verified and the saved byte count. Text: "+txt
open('scratch/d10_IDX-0003-01.txt','w',encoding='utf-8',newline='\n').write(ins)
print(len(txt.encode('utf-8')), "bytes")
