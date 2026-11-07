"""SmartRecruiters public Posting API — unauthenticated GET.
https://developers.smartrecruiters.com/reference/postingapisearch
The list endpoint returns titles + locations (no description); that's enough for
title/location matching. We avoid a detail call per posting to stay fast and free.
"""
from __future__ import annotations

import requests

from .base import Collector, RawJob

API = "https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={offset}"


def _loc(d: dict) -> str:
    if not isinstance(d, dict):
        return ""
    parts = [d.get("city"), d.get("region"), d.get("country", "").upper() if d.get("country") else None]
    return ", ".join(p for p in parts if p)


class SmartRecruitersCollector(Collector):
    source = "smartrecruiters"

    def fetch(self, slug: str) -> list[RawJob]:
        out: list[RawJob] = []
        offset = 0
        for _ in range(5):  # up to 500 postings, then stop
            r = requests.get(API.format(slug=slug, offset=offset), timeout=20)
            if r.status_code != 200:
                break
            content = r.json().get("content", [])
            if not content:
                break
            for j in content:
                out.append(
                    RawJob(
                        source=self.source,
                        external_id=str(j.get("id")),
                        title=(j.get("name") or "").strip(),
                        location=_loc(j.get("location", {})),
                        url=f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}",
                        description="",
                        posted_at=j.get("releasedDate"),
                        company_name=slug,
                    )
                )
            if len(content) < 100:
                break
            offset += 100
        return out
