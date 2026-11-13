"""Count the words of the ten proposal answers and render the proposal PDF.

Usage: python tools/proposal_pdf.py [--check-only]
Reads submission/PROPOSAL.md, enforces the 500-word limit on the ten substantive answers,
writes submission/cerbero-guardian-proposal.pdf with PyMuPDF and verifies it with pypdf.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "submission" / "PROPOSAL.md"
TARGET = ROOT / "submission" / "cerbero-guardian-proposal.pdf"
WORD_LIMIT, PDF_LIMIT = 500, 1024 * 1024
QUESTIONS = [
    "One sentence: What does the Skill do?",
    "Who is the target user and problem?",
    "What is your proposed solution?",
    "What is the Core User Flow?",
    "What substantive difference does your idea offer compared with existing tools or conventional AI solutions?",
    "Which UGREEN AI NAS capabilities will be used, and at which step in the workflow?",
    "What was your technical approach?",
    "What is the current development status?",
    "What is your final validation plan?",
    "Are there any known limitations of your Project?",
]


def sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    return [(p.split("\n", 1)[0].strip(), p.split("\n", 1)[1].strip()) for p in parts]


def words(text: str) -> int:
    plain = re.sub(r"[`*_]", "", text)
    return sum(1 for token in plain.split() if re.search(r"[A-Za-z0-9]", token))


def count(text: str) -> dict:
    found = sections(text)
    answers = {}
    for n, question in enumerate(QUESTIONS, start=1):
        match = [body for head, body in found if head == f"{n}. {question}"]
        if len(match) != 1:
            raise ValueError(f"question {n} missing or duplicated: {question}")
        answers[n] = words(match[0])
    return {"per_answer": answers, "total": sum(answers.values())}


STYLES = {"h1": ("hebo", 15.0, 6.0), "h2": ("hebo", 10.4, 7.0), "p": ("helv", 9.6, 3.0)}
MARGIN_X, MARGIN_Y = 50.0, 46.0


def blocks(text: str) -> list[tuple[str, str]]:
    out = []
    for line in text.splitlines():
        plain = re.sub(r"[`*]", "", line).strip()
        if line.startswith("# "):
            out.append(("h1", plain[2:]))
        elif line.startswith("## "):
            out.append(("h2", plain[3:]))
        elif plain:
            out.append(("p", plain))
    return out


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    import fitz

    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and fitz.get_text_length(trial, fontname=font, fontsize=size) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    return lines + ([current] if current else [])


def render(text: str) -> None:
    """Base-14 Helvetica only: no embedded fonts, no ligatures, clean text extraction."""
    import fitz

    doc = fitz.open()
    width, height = fitz.paper_size("a4")
    page, y = doc.new_page(width=width, height=height), MARGIN_Y
    for kind, content in blocks(text):
        font, size, gap = STYLES[kind]
        leading = size * 1.3
        lines = wrap(content, font, size, width - 2 * MARGIN_X)
        y += gap if kind != "p" else 0
        if y + leading * min(len(lines), 2) > height - MARGIN_Y:
            page, y = doc.new_page(width=width, height=height), MARGIN_Y
        for line in lines:
            if y + leading > height - MARGIN_Y:
                page, y = doc.new_page(width=width, height=height), MARGIN_Y
            y += leading
            color = (0.11, 0.23, 0.35) if kind == "h2" else (0, 0, 0)
            page.insert_text((MARGIN_X, y), line, fontname=font, fontsize=size, color=color)
        y += gap
    doc.set_metadata({"title": "Cerbero - UGREEN Hackathon 2026 proposal", "author": "Cerbero entrant"})
    doc.save(str(TARGET), garbage=4, deflate=True)
    doc.close()


def verify(text: str) -> dict:
    from pypdf import PdfReader

    with open(TARGET, "rb") as handle:
        reader = PdfReader(handle)
        pages = len(reader.pages)
        extracted = re.sub(r"\s+", " ", " ".join(page.extract_text() for page in reader.pages))
    missing = []
    for head, body in sections(text):
        probe = " ".join(re.sub(r"[`*_]", "", body).split()[:8])
        if probe not in extracted:
            missing.append(head)
    size = TARGET.stat().st_size
    if size > PDF_LIMIT or missing:
        raise RuntimeError(f"PDF check failed: size={size} missing={missing}")
    return {"pages": pages, "bytes": size, "pdf_words_total": words(extracted)}


def main(argv: list[str]) -> int:
    text = SOURCE.read_text(encoding="utf-8")
    counts = count(text)
    print(f"words per answer: {counts['per_answer']}  total: {counts['total']} / {WORD_LIMIT}")
    if counts["total"] > WORD_LIMIT:
        return 1
    if "--check-only" in argv:
        return 0
    render(text)
    print(f"{TARGET.relative_to(ROOT)}: {verify(text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
