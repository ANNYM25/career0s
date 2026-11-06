"""Generate cover-letter .docx files (free, via python-docx). The candidate's
two base CVs live in _private/ and are attached as-is — never rewritten per job.
"""
from __future__ import annotations

from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"
CL_DIR = VAULT / "06_Applications" / "Cover_Letters"


def write_cover_letter_docx(company: str, role: str, body: str, job_id: int) -> Path:
    from docx import Document  # imported lazily so the dep is optional at import time

    CL_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()
    doc.add_paragraph("[Your Name]")
    doc.add_paragraph("[Your Address] · [Email] · [Phone]")
    doc.add_paragraph("")
    doc.add_paragraph("[Date]")
    doc.add_paragraph("")
    doc.add_paragraph(f"Dear {company} Hiring Team,")
    doc.add_paragraph("")
    for para in (body or "").split("\n\n"):
        if para.strip():
            doc.add_paragraph(para.strip())
    doc.add_paragraph("")
    doc.add_paragraph("Yours sincerely,")
    doc.add_paragraph("[Your Name]")

    safe = "".join(c for c in f"{company}_{role}" if c.isalnum() or c in " _-")[:60].strip()
    path = CL_DIR / f"{safe}__{job_id}.docx"
    doc.save(path)
    return path
