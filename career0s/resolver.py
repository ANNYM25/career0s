"""Resolve companies to public ATS board tokens.

Most big brands use branded portals or Workday (no clean public API), but a large
share of fintechs / scaleups use Greenhouse or Lever, whose board token is usually
a predictable slug of the company name. We probe candidate slugs against the free
public endpoints and record any that respond. Fully free, no keys.
"""
from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .db import connect

LEGAL = re.compile(r"\b(inc|incorporated|ltd|limited|plc|llc|llp|group|holding|holdings|ag|sa|se|nv|bv|co|corp|corporation|company|partners|international|the)\b", re.I)


def slug_candidates(name: str) -> list[str]:
    base = name.lower().strip()
    base = base.replace("&", " and ")
    stripped = LEGAL.sub(" ", base)
    cands = set()
    for src in (base, stripped):
        s = re.sub(r"[^a-z0-9 ]", "", src).strip()
        if not s:
            continue
        words = s.split()
        cands.add(s.replace(" ", ""))          # "procter-gamble" -> "proctergamble"
        cands.add(s.replace(" ", "-"))         # "procter-gamble"
        if len(words) == 1:
            cands.add(words[0])                # single-word names only; avoids
                                               # "Oliver Wyman" -> "oliver" mismatches
    # Require length >= 4 to cut generic short tokens.
    return [c for c in cands if len(c) >= 4][:6]


def probe_greenhouse(slug: str) -> int | None:
    try:
        r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=8)
        if r.status_code == 200:
            n = len(r.json().get("jobs", []))
            return n if n > 0 else None
    except requests.RequestException:
        pass
    return None


def probe_lever(slug: str) -> int | None:
    try:
        r = requests.get(f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=8)
        if r.status_code == 200:
            n = len(r.json())
            return n if n > 0 else None
    except requests.RequestException:
        pass
    return None


def probe_ashby(slug: str) -> int | None:
    try:
        r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=8)
        if r.status_code == 200:
            n = len(r.json().get("jobs", []))
            return n if n > 0 else None
    except requests.RequestException:
        pass
    return None


def probe_smartrecruiters(slug: str) -> int | None:
    try:
        r = requests.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1", timeout=8)
        if r.status_code == 200:
            n = r.json().get("totalFound", 0)
            return n if n > 0 else None
    except requests.RequestException:
        pass
    return None


# Order matters: cleaner/tighter boards first.
PROBES = [
    ("greenhouse", probe_greenhouse),
    ("ashby", probe_ashby),
    ("lever", probe_lever),
    ("smartrecruiters", probe_smartrecruiters),
]


def resolve_company(cid: int, name: str) -> tuple[int, str, str, int] | None:
    for slug in slug_candidates(name):
        for ats, probe in PROBES:
            n = probe(slug)
            if n:
                return (cid, ats, slug, n)
    return None


def resolve_all(owner: str = "Anny", workers: int = 12) -> int:
    conn = connect()
    rows = conn.execute(
        "SELECT id, name FROM companies WHERE owner=? AND (ats='unknown' OR ats_slug IS NULL)",
        (owner,),
    ).fetchall()
    found = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(resolve_company, r["id"], r["name"]): r["name"] for r in rows}
        for fut in as_completed(futs):
            res = fut.result()
            if res:
                cid, ats, slug, n = res
                conn.execute("UPDATE companies SET ats=?, ats_slug=? WHERE id=?", (ats, slug, cid))
                found += 1
                print(f"  ✓ {futs[fut]:<34} {ats}:{slug} ({n} jobs)")
    conn.commit()
    conn.close()
    print(f"Resolved {found} / {len(rows)} companies to a public ATS feed.")
    return found


if __name__ == "__main__":
    resolve_all()
