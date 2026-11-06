"""Local LLM via Ollama — free, offline, no API key. Used for optional match
re-ranking and cover-letter drafting. Everything degrades gracefully: if Ollama
is unavailable the pipeline still runs deterministically.
"""
from __future__ import annotations

import json

import requests


class Ollama:
    def __init__(self, model: str = "qwen2.5:7b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def available(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def generate(self, prompt: str, system: str | None = None, fmt: str | None = None, timeout: int = 120) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system
        if fmt:
            payload["format"] = fmt
        r = requests.post(f"{self.host}/api/generate", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json().get("response", "").strip()

    def score_match(self, profile: str, job_title: str, job_desc: str) -> tuple[int, str]:
        """Return (0-100, one-line reason) for fit against the profile."""
        system = (
            "You are a career matching assistant for an early-career candidate in "
            "sustainable finance / FinTech. Rate how well a job fits. Return JSON "
            'only: {"score": <0-100>, "reason": "<one sentence>"}.'
        )
        prompt = (
            f"CANDIDATE PROFILE:\n{profile}\n\n"
            f"JOB TITLE: {job_title}\n"
            f"JOB DESCRIPTION (truncated):\n{job_desc[:2500]}\n\n"
            "Rate the fit. Favour entry-level, sustainable-finance / FP&A / FinTech roles "
            "in Europe. Penalise senior roles and unrelated fields."
        )
        try:
            raw = self.generate(prompt, system=system, fmt="json", timeout=90)
            data = json.loads(raw)
            return int(data.get("score", 0)), str(data.get("reason", ""))[:300]
        except (requests.RequestException, json.JSONDecodeError, ValueError, KeyError):
            return -1, ""

    def cover_letter(self, profile: str, company: str, job_title: str, job_desc: str) -> str:
        system = (
            "You write concise, specific, professional cover letters for an "
            "early-career candidate. 4 short paragraphs, no clichés, no placeholders "
            "left unfilled except [NAME] / [DATE]. British English."
        )
        prompt = (
            f"CANDIDATE PROFILE:\n{profile}\n\n"
            f"COMPANY: {company}\nROLE: {job_title}\n"
            f"JOB DESCRIPTION:\n{job_desc[:3000]}\n\n"
            "Write the cover letter body only."
        )
        return self.generate(prompt, system=system, timeout=180)
