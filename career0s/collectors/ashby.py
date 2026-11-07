"""Ashby public job-board API — unauthenticated GET.
https://developers.ashbyhq.com/docs/public-job-posting-api
"""
from __future__ import annotations

import re

import requests

from .base import Collector, RawJob

API = "https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=false"


def _strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


class AshbyCollector(Collector):
    source = "ashby"

    def fetch(self, slug: str) -> list[RawJob]:
        r = requests.get(API.format(slug=slug), timeout=20)
        if r.status_code != 200:
            return []
        out: list[RawJob] = []
        for j in r.json().get("jobs", []):
            if j.get("isListed") is False:
                continue
            desc = j.get("descriptionPlain") or _strip_html(j.get("descriptionHtml", ""))
            out.append(
                RawJob(
                    source=self.source,
                    external_id=str(j.get("id")),
                    title=(j.get("title") or "").strip(),
                    location=j.get("location", ""),
                    url=j.get("jobUrl") or j.get("applyUrl", ""),
                    description=desc[:8000],
                    posted_at=j.get("publishedAt"),
                    company_name=slug,
                )
            )
        return out
