"""Write one Markdown record per job into the Obsidian vault. Obsidian reads
plain Markdown from the local filesystem — no subscription, fully private.
"""
from __future__ import annotations

import re
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"
JOBS_DIR = VAULT / "01_Jobs"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def write_job_note(job: dict) -> Path:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{_slug(job['company_name'])}__{_slug(job['title'])}__{job['id']}.md"
    path = JOBS_DIR / fname
    fm = {
        "company": job.get("company_name", ""),
        "role": job.get("title", ""),
        "location": job.get("location", ""),
        "source": job.get("source", ""),
        "status": job.get("status", "new"),
        "match_score": job.get("score", 0),
        "llm_score": job.get("llm_score") or "",
        "role_family": job.get("role_family") or "",
        "posted_at": job.get("posted_at") or "",
        "application_url": job.get("url", ""),
    }
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {v}")
    lines += [
        "---",
        f"# {job.get('title','')} — {job.get('company_name','')}",
        "",
        f"**Score:** {job.get('score',0)}/100  ·  **Family:** {job.get('role_family') or '—'}",
        f"**Location:** {job.get('location','')}",
        f"**Apply:** {job.get('url','')}",
        "",
        "## Why it matched",
        job.get("llm_reason") or "_deterministic match_",
        "",
        "## Checklist",
        "- [ ] Read full description",
        "- [ ] Confirm eligibility / work rights",
        "- [ ] Select CV (1 of 2)",
        "- [ ] Review generated cover letter",
        "- [ ] Prepare application answers",
        "- [ ] **Submit manually (human approval)**",
        "",
        "## Description",
        job.get("description", "")[:4000],
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
