"""Shared types for collectors."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RawJob:
    source: str
    external_id: str
    title: str
    location: str
    url: str
    description: str = ""
    posted_at: str | None = None
    company_name: str = ""
    extra: dict = field(default_factory=dict)


class Collector:
    """Base collector. Subclasses implement fetch(slug) -> list[RawJob]."""

    source = "base"

    def fetch(self, slug: str) -> list[RawJob]:  # pragma: no cover - interface
        raise NotImplementedError
