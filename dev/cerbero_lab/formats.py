"""Deterministic, valid-format synthetic files for the demo: a one-page PDF, a DOCX and an RGB TIFF.

Standard library only. The bytes depend only on the arguments, so digests are stable across runs.
Each generator has a structural check used by the tests and by make_demo_dataset.py.
"""
from __future__ import annotations

import hashlib
import io
import re
import struct
import zipfile
from xml.etree import ElementTree


def pdf(text: str) -> bytes:
    """A one-page PDF 1.4 with the text in Helvetica, with a correct cross-reference table."""
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    lines = [f"BT /F1 14 Tf 72 {760 - 22 * n} Td ({line}) Tj ET" for n, line in enumerate(safe.split("\n"))]
    stream = "\n".join(lines).encode("latin-1")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
               b"/Resources << /Font << /F1 5 0 R >> >> >>",
               b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(b"%d 0 obj\n" % number + body + b"\nendobj\n")
    xref = out.tell()
    out.write(b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1))
    for offset in offsets:
        out.write(b"%010d 00000 n \n" % offset)
    out.write(b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref))
    return out.getvalue()


def check_pdf(data: bytes) -> bool:
    if not data.startswith(b"%PDF-1.") or not data.rstrip().endswith(b"%%EOF"):
        return False
    start = int(re.findall(rb"startxref\n(\d+)\n", data)[-1])
    if not data[start:].startswith(b"xref\n"):
        return False
    entries = re.findall(rb"(\d{10}) 00000 n ", data[start:])
    return all(data[int(o):].startswith(b"%d 0 obj" % n) for n, o in enumerate(entries, start=1))


_CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                  '<Default Extension="xml" ContentType="application/xml"/>'
                  '<Override PartName="/word/document.xml" '
                  'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
         'Target="word/document.xml"/></Relationships>')
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def docx(text: str) -> bytes:
    """A minimal Word document: content types, package relationship and one paragraph per line."""
    paragraphs = "".join(f"<w:p><w:r><w:t xml:space=\"preserve\">{line}</w:t></w:r></w:p>"
                         for line in (text.replace("&", "&amp;").replace("<", "&lt;").split("\n")))
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{_W}">'
                f"<w:body>{paragraphs}</w:body></w:document>")
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, body in (("[Content_Types].xml", _CONTENT_TYPES), ("_rels/.rels", _RELS),
                           ("word/document.xml", document)):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, body)
    return out.getvalue()


def docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        if {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} - set(package.namelist()):
            raise ValueError("incomplete DOCX package")
        root = ElementTree.fromstring(package.read("word/document.xml"))
    return "\n".join("".join(t.text or "" for t in p.iter(f"{{{_W}}}t")) for p in root.iter(f"{{{_W}}}p"))


def tiff(seed: str, width: int = 64, height: int = 48, mark: bool = False) -> bytes:
    """An uncompressed 8-bit RGB baseline TIFF. mark=True changes a pixel block, keeping the size."""
    key = hashlib.sha256(seed.encode()).digest()
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            pixels += bytes(((x * 4 + key[0]) % 256, (y * 5 + key[1]) % 256, ((x + y) * 3 + key[2]) % 256))
    if mark:
        for y in range(8, 16):
            for x in range(8, 16):
                i = (y * width + x) * 3
                pixels[i:i + 3] = b"\xff\x00\xff"
    entries = 12
    ifd = 8
    extra = ifd + 2 + entries * 12 + 4
    bits, xres, yres = extra, extra + 6, extra + 14
    data_offset = extra + 22
    tags = [(256, 3, 1, width), (257, 3, 1, height), (258, 3, 3, bits), (259, 3, 1, 1), (262, 3, 1, 2),
            (273, 4, 1, data_offset), (277, 3, 1, 3), (278, 3, 1, height), (279, 4, 1, len(pixels)),
            (282, 5, 1, xres), (283, 5, 1, yres), (296, 3, 1, 2)]
    out = bytearray(b"II*\x00" + struct.pack("<I", ifd))
    out += struct.pack("<H", entries)
    for tag, kind, count, value in tags:
        packed = struct.pack("<HI", value, 0)[:4] if kind == 3 and count == 1 else struct.pack("<I", value)
        out += struct.pack("<HHI", tag, kind, count) + packed
    out += struct.pack("<I", 0)
    out += struct.pack("<HHH", 8, 8, 8) + struct.pack("<II", 72, 1) + struct.pack("<II", 72, 1)
    out += pixels
    return bytes(out)


def check_tiff(data: bytes) -> tuple[int, int]:
    """Parse the header and IFD; return (width, height) when the strip fits the declared size."""
    if data[:4] != b"II*\x00":
        raise ValueError("not a little-endian TIFF")
    ifd = struct.unpack_from("<I", data, 4)[0]
    count = struct.unpack_from("<H", data, ifd)[0]
    tags = {}
    for n in range(count):
        tag, kind, items, value = struct.unpack_from("<HHII", data, ifd + 2 + 12 * n)
        tags[tag] = value & 0xFFFF if kind == 3 and items == 1 else value
    width, height, offset, length = tags[256], tags[257], tags[273], tags[279]
    if tags[259] != 1 or tags[262] != 2 or length != width * height * 3 or offset + length != len(data):
        raise ValueError("unexpected TIFF layout")
    return width, height
