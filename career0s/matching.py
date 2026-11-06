"""Deterministic matching + scoring. Fast, explainable, free — runs before any
optional LLM re-rank. A job must clear the seniority gate and match at least one
role family to be shortlisted.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class ScoreResult:
    score: int
    role_family: str | None
    reasons: list[str]
    passed: bool


def _contains_any(text: str, needles: list[str]) -> list[str]:
    t = text.lower()
    return [n for n in needles if n.lower() in t]


def score_job(title: str, description: str, location: str, posted_at: str | None, cfg: dict) -> ScoreResult:
    w = cfg["scoring"]
    reasons: list[str] = []
    score = 0

    # 1) Seniority gate (hard filter on exclusions in the TITLE).
    excl = _contains_any(title, cfg["seniority_exclude"])
    if excl:
        return ScoreResult(0, None, [f"excluded seniority: {', '.join(excl)}"], False)

    # 2) Role family. A keyword in the TITLE earns full weight; a keyword only in
    #    the description earns half (it's often boilerplate, e.g. a consultancy's
    #    "we care about sustainability" blurb on an IT role). Pick highest priority.
    best_family = None
    best_priority = 99
    best_in_title = False
    for fam in cfg["role_families"]:
        in_title = bool(_contains_any(title, fam["keywords"]))
        in_desc = bool(_contains_any(description, fam["keywords"]))
        if (in_title or in_desc) and fam["priority"] < best_priority:
            best_priority = fam["priority"]
            best_family = fam["name"]
            best_in_title = in_title
    if not best_family:
        return ScoreResult(0, None, ["no role-family keyword match"], False)
    base = w["role_family_match"] * (1 - 0.1 * (best_priority - 1))
    if not best_in_title:
        base *= 0.5
        reasons.append(f"role family (desc only): {best_family}")
    else:
        reasons.append(f"role family: {best_family}")
    score += int(base)

    # 3) Seniority fit (positive signal, title only).
    incl = _contains_any(title, cfg["seniority_include"])
    if incl:
        score += w["seniority_fit"]
        reasons.append(f"entry-level signal: {', '.join(incl[:3])}")

    # 4) Location fit — ONLY from the job's location field, never the description
    #    (description mentions of "Europe" caused non-EU roles to score high).
    loc = _contains_any(location, cfg["locations_include"])
    if loc:
        score += w["location_fit"]
        reasons.append(f"location: {', '.join(sorted(set(loc))[:3])}")
    elif location and location.strip():
        reasons.append(f"location off-target: {location[:40]}")

    # 5) Freshness.
    if posted_at:
        try:
            d = dt.datetime.fromisoformat(posted_at.replace("Z", "+00:00")).replace(tzinfo=None)
            if (dt.datetime.utcnow() - d).days <= 14:
                score += w["freshness"]
                reasons.append("posted within 14 days")
        except (ValueError, AttributeError):
            pass

    score = min(score, 100)
    passed = score >= w["min_shortlist_score"]
    return ScoreResult(score, best_family, reasons, passed)
