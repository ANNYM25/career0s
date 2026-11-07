"""Career0S command-line interface.

Commands:
  import                 Load the target-universe workbook into SQLite
  discover               Fetch jobs from public ATS feeds for known companies
  match                  Score + shortlist jobs (deterministic, optional LLM)
  notes                  Write Obsidian markdown records for shortlisted jobs
  report                 Write the daily opportunity report
  run                    discover -> match -> notes -> report (the daily job)
  prepare <job_id>       Open the posting and prep the application (Playwright)
  stats                  Show database counts
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from . import db as _db
from .collectors import REGISTRY
from .importer import import_workbook
from .llm import Ollama
from .matching import score_job
from .obsidian import write_job_note
from .report import write_daily_report

console = Console()
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "anny.yaml"
PROFILE_SUMMARY = Path(__file__).resolve().parent.parent / "_private" / "profile_summary.txt"


def load_cfg() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text())


def cmd_import(args):
    import_workbook(workbook=getattr(args, "workbook", None), owner=args.owner)


def cmd_setup_vault(args):
    import shutil
    root = Path(__file__).resolve().parent.parent
    tpl = root / "templates"
    vault = root / "vault"
    copied = 0
    for src in tpl.rglob("*.md"):
        dest = vault / src.relative_to(tpl)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():          # never overwrite the user's own notes
            shutil.copy2(src, dest)
            copied += 1
    console.print(f"[green]Vault ready. Copied {copied} template(s) into vault/.[/]")


def cmd_resolve(args):
    from .resolver import resolve_all
    resolve_all(owner=args.owner)


def cmd_discover(args):
    conn = _db.connect()
    placeholders = ",".join("?" * len(REGISTRY))
    companies = conn.execute(
        f"SELECT * FROM companies WHERE owner=? AND ats IN ({placeholders}) AND ats_slug IS NOT NULL",
        (args.owner, *REGISTRY.keys()),
    ).fetchall()
    console.print(f"[cyan]{len(companies)} companies with a known public ATS feed[/]")
    total = 0
    for c in companies:
        collector = REGISTRY[c["ats"]]()
        try:
            jobs = collector.fetch(c["ats_slug"])
        except Exception as e:  # noqa: BLE001
            console.print(f"  [red]{c['name']}: {e}[/]")
            continue
        for j in jobs:
            conn.execute(
                """INSERT OR IGNORE INTO jobs
                   (company_id, company_name, source, external_id, title, location, description, url, posted_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (c["id"], c["name"], j.source, j.external_id, j.title, j.location, j.description, j.url, j.posted_at),
            )
            total += 1
        if jobs:
            console.print(f"  {c['name']}: {len(jobs)} postings")
    conn.commit()
    console.print(f"[green]Discovery done. {total} postings seen.[/]")
    conn.close()


def cmd_match(args):
    cfg = load_cfg()
    conn = _db.connect()
    use_llm = cfg["llm"]["enabled"] and not args.no_llm
    ol = Ollama(cfg["llm"]["model"], cfg["llm"]["host"]) if use_llm else None
    if ol and not ol.available():
        console.print("[yellow]Ollama not reachable — running deterministic only.[/]")
        ol = None
    profile = PROFILE_SUMMARY.read_text() if PROFILE_SUMMARY.exists() else \
        "Early-career candidate, Sustainable Finance & FinTech focus, Europe, entry-level/internship."

    rows = conn.execute("SELECT * FROM jobs WHERE status='new'").fetchall()
    console.print(f"[cyan]Scoring {len(rows)} new jobs[/]")
    shortlisted = 0
    for r in rows:
        res = score_job(r["title"], r["description"], r["location"], r["posted_at"], cfg)
        llm_score, llm_reason = (None, None)
        if res.passed and ol:
            s, reason = ol.score_match(profile, r["title"], r["description"])
            if s >= 0:
                llm_score, llm_reason = s, reason
        status = "shortlisted" if res.passed else "rejected"
        if res.passed:
            shortlisted += 1
        conn.execute(
            "UPDATE jobs SET score=?, role_family=?, llm_score=?, llm_reason=?, status=? WHERE id=?",
            (res.score, res.role_family, llm_score, llm_reason or "; ".join(res.reasons), status, r["id"]),
        )
    conn.commit()
    console.print(f"[green]Shortlisted {shortlisted} / {len(rows)}.[/]")
    conn.close()


def cmd_notes(args):
    conn = _db.connect()
    rows = conn.execute("SELECT * FROM jobs WHERE status='shortlisted' ORDER BY score DESC").fetchall()
    for r in rows:
        write_job_note(dict(r))
    console.print(f"[green]Wrote {len(rows)} job notes to the vault.[/]")
    conn.close()


def cmd_report(args):
    conn = _db.connect()
    path = write_daily_report(conn)
    console.print(f"[green]Daily report: {path}[/]")
    conn.close()


def cmd_run(args):
    cmd_discover(args)
    cmd_match(args)
    cmd_notes(args)
    cmd_report(args)


def cmd_prepare(args):
    from .apply import prepare_application
    conn = _db.connect()
    r = conn.execute("SELECT * FROM jobs WHERE id=?", (args.job_id,)).fetchone()
    if not r:
        console.print("[red]No such job id.[/]")
        return
    console.print(f"[cyan]Preparing: {r['title']} @ {r['company_name']}[/]")
    prepare_application(r["url"], cv_path=args.cv)
    conn.execute("UPDATE jobs SET status='prepared' WHERE id=?", (args.job_id,))
    conn.commit()
    conn.close()


def cmd_stats(args):
    conn = _db.connect()
    t = Table(title="Career0S")
    t.add_column("metric"); t.add_column("value", justify="right")
    t.add_row("companies", str(conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]))
    for st in ["new", "shortlisted", "rejected", "prepared", "applied"]:
        t.add_row(f"jobs: {st}", str(conn.execute("SELECT COUNT(*) FROM jobs WHERE status=?", (st,)).fetchone()[0]))
    console.print(t)
    conn.close()


def main(argv=None):
    p = argparse.ArgumentParser(prog="career0s", description="Zero-cost career acquisition system")
    p.add_argument("--owner", default="Anny")
    sub = p.add_subparsers(dest="cmd", required=True)
    imp = sub.add_parser("import"); imp.add_argument("--workbook", help="path to an .xlsx (default: newest in data/)"); imp.set_defaults(func=cmd_import)
    sub.add_parser("setup-vault").set_defaults(func=cmd_setup_vault)
    sub.add_parser("resolve").set_defaults(func=cmd_resolve)
    d = sub.add_parser("discover"); d.set_defaults(func=cmd_discover)
    m = sub.add_parser("match"); m.add_argument("--no-llm", action="store_true"); m.set_defaults(func=cmd_match)
    sub.add_parser("notes").set_defaults(func=cmd_notes)
    sub.add_parser("report").set_defaults(func=cmd_report)
    r = sub.add_parser("run"); r.add_argument("--no-llm", action="store_true"); r.set_defaults(func=cmd_run)
    pr = sub.add_parser("prepare"); pr.add_argument("job_id", type=int); pr.add_argument("--cv"); pr.set_defaults(func=cmd_prepare)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
