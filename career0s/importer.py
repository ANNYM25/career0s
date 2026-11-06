"""Import the target-universe workbook into SQLite.

Reads the per-person sheets (default: Anny) and seeds the `companies` table,
guessing each company's ATS from its careers URL where possible.
"""
from __future__ import annotations

import re
from pathlib import Path

import openpyxl

from .db import connect

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_WORKBOOK = DATA_DIR / "Anny_Anish_Expanded_Target_Universe_2026.xlsx"


def find_workbook() -> Path:
    """Use the default workbook if present, else the newest .xlsx in data/."""
    if DEFAULT_WORKBOOK.exists():
        return DEFAULT_WORKBOOK
    xlsx = sorted(DATA_DIR.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not xlsx:
        raise FileNotFoundError(
            f"No .xlsx found in {DATA_DIR}. Put your target-company workbook there."
        )
    return xlsx[0]


def _find_header(rows: list[tuple], key: str = "Company") -> int:
    for i, r in enumerate(rows):
        if r and any(isinstance(c, str) and c.strip() == key for c in r):
            return i
    raise ValueError(f"No header row containing {key!r}")


def _col_map(header: tuple) -> dict[str, int]:
    out = {}
    for i, c in enumerate(header):
        if isinstance(c, str) and c.strip():
            out[c.strip().lower()] = i
    return out


def guess_ats(url: str | None) -> tuple[str, str | None]:
    """Return (ats, slug). Slug is the board token used by the public API."""
    if not url:
        return "unknown", None
    u = url.lower()
    m = re.search(r"boards\.greenhouse\.io/([a-z0-9_-]+)", u) or re.search(r"greenhouse\.io/embed/job_board\?for=([a-z0-9_-]+)", u)
    if m:
        return "greenhouse", m.group(1)
    m = re.search(r"jobs\.lever\.co/([a-z0-9_-]+)", u)
    if m:
        return "lever", m.group(1)
    if "myworkdayjobs.com" in u or "workday" in u:
        return "workday", None
    if "smartrecruiters.com" in u:
        return "smartrecruiters", None
    if "icims.com" in u:
        return "icims", None
    return "unknown", None


def _get(row, cmap, *names):
    for n in names:
        i = cmap.get(n)
        if i is not None and i < len(row) and row[i] not in (None, ""):
            return str(row[i]).strip()
    return None


def import_workbook(workbook: Path | str | None = None, owner: str = "Anny") -> int:
    workbook = Path(workbook) if workbook else find_workbook()
    print(f"Reading workbook: {workbook.name}")
    wb = openpyxl.load_workbook(workbook, read_only=True, data_only=True)
    conn = connect()
    inserted = 0

    # Prefer this person's richest sheet; fall back to First Wave; and if neither
    # exists (a differently-structured workbook), use ANY sheet that has a
    # "Company" column.
    sheet_candidates = [f"{owner} Master Targets", f"{owner} First Wave"]
    sheets = [s for s in sheet_candidates if s in wb.sheetnames]
    if not sheets:
        for s in wb.sheetnames:
            rows = [r for r in wb[s].iter_rows(values_only=True)]
            if any(r and any(isinstance(c, str) and c.strip() == "Company" for c in r) for r in rows[:10]):
                sheets.append(s)
        print(f"No '{owner}' sheets found; using sheets with a Company column: {sheets}")

    seen: set[str] = set()
    for sheet in sheets:
        ws = wb[sheet]
        rows = [r for r in ws.iter_rows(values_only=True)]
        hi = _find_header(rows)
        cmap = _col_map(rows[hi])
        is_first_wave = "rank" in cmap
        for r in rows[hi + 1:]:
            if not r or not r[cmap["company"]]:
                continue
            name = str(r[cmap["company"]]).strip()
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            careers = _get(r, cmap, "careers / vacancy check", "official careers portal", "careers / vacancy check ")
            ats, slug = guess_ats(careers)
            rank = None
            if is_first_wave and cmap.get("rank") is not None:
                try:
                    rank = int(r[cmap["rank"]])
                except (TypeError, ValueError):
                    rank = None
            conn.execute(
                """INSERT OR IGNORE INTO companies
                   (name, owner, source_list, sector, markets, priority, role_angle, careers_url, ats, ats_slug, rank)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    name, owner,
                    _get(r, cmap, "source list"),
                    _get(r, cmap, "sector / category", "sector"),
                    _get(r, cmap, "market(s) / location", "market(s)"),
                    _get(r, cmap, "priority"),
                    _get(r, cmap, "target role angle", "role angle for this person"),
                    careers, ats, slug, rank,
                ),
            )
            inserted += conn.total_changes and 1 or 0
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM companies WHERE owner=?", (owner,)).fetchone()[0]
    by_ats = conn.execute(
        "SELECT ats, COUNT(*) c FROM companies WHERE owner=? GROUP BY ats ORDER BY c DESC", (owner,)
    ).fetchall()
    conn.close()
    print(f"Imported companies for {owner}: {n} total")
    for row in by_ats:
        print(f"  {row['ats']:<16} {row['c']}")
    return n


if __name__ == "__main__":
    import_workbook()
