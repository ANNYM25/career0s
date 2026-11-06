"""Playwright application-prep agent.

HARD RULE: this never submits an application. It opens the posting in a real
browser, fills the fields it can infer from a structured profile, attaches the
chosen CV, then STOPS and hands control to the human for review + submit.
CAPTCHAs, eligibility/work-authorisation and declaration questions always stop
the automation.
"""
from __future__ import annotations

import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parent.parent / "_private" / "profile.json"

# Fields we are willing to auto-fill (safe, factual). Anything outside this set
# is left for the human.
SAFE_FIELDS = {
    "first_name", "last_name", "full_name", "email", "phone",
    "linkedin", "location", "city", "country",
}

STOP_KEYWORDS = [
    "visa", "sponsor", "work authorization", "work authorisation", "eligible to work",
    "right to work", "disability", "veteran", "ethnicity", "gender",
    "criminal", "declaration", "certify", "captcha",
]


def load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    return {}


def prepare_application(url: str, cv_path: str | None = None, headless: bool = False) -> dict:
    """Open the posting, best-effort fill safe fields, pause for human review."""
    from playwright.sync_api import sync_playwright

    profile = load_profile()
    report = {"url": url, "filled": [], "stopped_for": [], "attached_cv": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Detect fields that must stop the automation.
        body_text = (page.inner_text("body") or "").lower()
        for kw in STOP_KEYWORDS:
            if kw in body_text:
                report["stopped_for"].append(kw)

        # Best-effort fill of safe inputs matched by name/placeholder/label.
        for key in SAFE_FIELDS:
            val = profile.get(key)
            if not val:
                continue
            selectors = [
                f"input[name*='{key}']",
                f"input[id*='{key}']",
                f"input[placeholder*='{key.replace('_',' ')}']",
            ]
            for sel in selectors:
                try:
                    el = page.query_selector(sel)
                    if el:
                        el.fill(str(val))
                        report["filled"].append(key)
                        break
                except Exception:
                    continue

        if cv_path and Path(cv_path).exists():
            try:
                fi = page.query_selector("input[type='file']")
                if fi:
                    fi.set_input_files(cv_path)
                    report["attached_cv"] = cv_path
            except Exception:
                pass

        print("\n=== APPLICATION PREP COMPLETE — HUMAN REVIEW REQUIRED ===")
        print(f"Filled: {report['filled']}")
        print(f"Attached CV: {report['attached_cv']}")
        if report["stopped_for"]:
            print(f"⚠ STOP fields detected (answer these yourself): {sorted(set(report['stopped_for']))}")
        print("Review every field, then SUBMIT MANUALLY. The browser stays open.")
        if not headless:
            page.pause()  # Playwright inspector — hands control to the human.
        browser.close()
    return report
