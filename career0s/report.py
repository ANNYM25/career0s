"""Daily opportunity report — a ranked shortlist written to the vault."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"
REPORTS = VAULT / "09_Reports" / "Daily"


def write_daily_report(conn, top_n: int = 25) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    rows = conn.execute(
        """SELECT company_name, title, location, score, llm_score, role_family, url, status
           FROM jobs
           WHERE status IN ('new','shortlisted')
           ORDER BY COALESCE(llm_score, score) DESC, score DESC
           LIMIT ?""",
        (top_n,),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    new_today = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE date(discovered_at)=date('now')"
    ).fetchone()[0]

    lines = [
        f"# Daily Opportunity Report — {today}",
        "",
        f"- Jobs in database: **{total}**",
        f"- Discovered today: **{new_today}**",
        f"- Shortlist shown: **{len(rows)}**",
        "",
        "| # | Score | Company | Role | Location | Family |",
        "|---|-------|---------|------|----------|--------|",
    ]
    for i, r in enumerate(rows, 1):
        s = r["llm_score"] if r["llm_score"] else r["score"]
        lines.append(
            f"| {i} | {s} | {r['company_name']} | [{r['title']}]({r['url']}) | {r['location']} | {r['role_family'] or '—'} |"
        )
    lines += ["", "> Review each, then prepare applications with `career0s prepare <job_id>`.", ""]
    path = REPORTS / f"{today}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
