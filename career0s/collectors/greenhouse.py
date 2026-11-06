"""Greenhouse public Job Board API — unauthenticated GET, explicitly public.
https://developers.greenhouse.io/job-board.html
"""
from __future__ import annotations

import re

import requests

from .base import Collector, RawJob

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#39;", "'")
    return re.sub(r"\s+", " ", text).strip()


class GreenhouseCollector(Collector):
    source = "greenhouse"

    def fetch(self, slug: str) -> list[RawJob]:
        r = requests.get(API.format(slug=slug), timeout=20)
        if r.status_code != 200:
            return []
        data = r.json()
        out: list[RawJob] = []
        for j in data.get("jobs", []):
            out.append(
                RawJob(
                    source=self.source,
                    external_id=str(j.get("id")),
                    title=j.get("title", ""),
                    location=(j.get("location") or {}).get("name", ""),
                    url=j.get("absolute_url", ""),
                    description=_strip_html(j.get("content", ""))[:8000],
                    posted_at=j.get("updated_at") or j.get("first_published"),
                    company_name=slug,
                )
            )
        return out
