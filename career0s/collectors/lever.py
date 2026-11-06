"""Lever public postings API — unauthenticated GET.
https://help.lever.co/hc/en-us/articles/360042870851
"""
from __future__ import annotations

import re

import requests

from .base import Collector, RawJob

API = "https://api.lever.co/v0/postings/{slug}?mode=json"


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


class LeverCollector(Collector):
    source = "lever"

    def fetch(self, slug: str) -> list[RawJob]:
        r = requests.get(API.format(slug=slug), timeout=20)
        if r.status_code != 200:
            return []
        out: list[RawJob] = []
        for j in r.json():
            cats = j.get("categories", {}) or {}
            posted = None
            if j.get("createdAt"):
                import datetime as _dt
                posted = _dt.datetime.utcfromtimestamp(j["createdAt"] / 1000).isoformat()
            out.append(
                RawJob(
                    source=self.source,
                    external_id=str(j.get("id")),
                    title=j.get("text", ""),
                    location=cats.get("location", ""),
                    url=j.get("hostedUrl", ""),
                    description=_strip_html(j.get("descriptionPlain") or j.get("description", ""))[:8000],
                    posted_at=posted,
                    company_name=slug,
                )
            )
        return out
