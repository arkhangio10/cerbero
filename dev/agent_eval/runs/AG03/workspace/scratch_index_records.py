BUNDLE_ID = "IDX-0002-01"
CASE_ID = "CAS-0002"
SCOPE_ID = "SCP-0001"
HINT = "CERBERO-IDX-0002-01"
OUT_MD = "index_bundle.md"
OUT_SH = "d10_index.sh"
RECS = []
entries = [
    ("/data/studio/cerbero-memory/CERBERO-B-0001-01.md", "B-0001-01", "22d927d38eabd5a2be1748dc9df31b3e09a4b524db937a5f386771d06dc1e19a", "current"),
    ("/data/studio/cerbero-memory/CERBERO-IDX-0001-01.md", "IDX-0001-01", "a3d040488be4350c408b1ebcd679f6cfbde3e7add74343ac9b45ff4bc5100918", "superseded"),
    ("/data/studio/cerbero-memory/CERBERO-B-0002-01.md", "B-0002-01", "bae492a21e01fc4b12fe1273e7c86a97c0a4eb43d813131e2d2d598b71ac3569", "current"),
    ("/data/studio/cerbero-memory/CERBERO-B-0002-02.md", "B-0002-02", "5ea2dc2bfbaa045c34b2c0b26268e4586e130a76b7fd6e960bf0994a65b6f3ac", "current"),
]
for i, (f, b, s, st) in enumerate(entries, 1):
    RECS.append(("IDX-0002-01-%04d" % i, dict(type="index-entry", file=f, bundle_id=b, sha256=s, status=st)))
