# Career0S — an open-source, zero-cost career acquisition system

Career0S turns a target-company list into a daily pipeline of **matched job
opportunities**, drafts the paperwork, and prepares applications for you — while
keeping every submission under **human control**. It runs entirely on your own
Mac, with **no paid APIs, no paid hosting, no paid scrapers**. €0.

Built for a 7-month run toward **June 2027**, focused on **Sustainable Finance /
FinTech** early-career roles across Europe.

```
Target universe ─▶ Job discovery ─▶ Matching & scoring ─▶ Application prep ─▶ YOUR approval
 (your Excel)      (public ATS       (rules + local        (cover letter +      (review &
                    APIs, free)        LLM, free)           Playwright form)     submit yourself)
```

## What it does

| Stage | How | Cost |
|-------|-----|------|
| Import 540 target companies | `openpyxl` reads your workbook | €0 |
| Find which have public job feeds | probe Greenhouse / Lever public APIs | €0 |
| Discover new vacancies daily | public ATS JSON APIs (no scraping of LinkedIn) | €0 |
| Score & shortlist | deterministic rules + optional local LLM (Ollama) | €0 |
| Write per-job notes | Markdown into an Obsidian vault | €0 |
| Daily opportunity report | ranked shortlist Markdown | €0 |
| Draft cover letters | `python-docx` + local LLM | €0 |
| Prepare applications | Playwright fills safe fields, **stops for you to submit** | €0 |

## The golden rule

**No application is ever submitted automatically.** Career0S fills the safe,
factual fields (name, email, phone), attaches one of your two CVs, drafts the
cover letter, then stops. Eligibility, work-authorisation, declarations and
CAPTCHAs always halt the automation for your review.

We also **do not** scrape or automate LinkedIn (profiles, connections, messages)
— it is against their terms and risks your account. Networking stays human; only
discovery is automated.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# put the workbook at data/<workbook>.xlsx (gitignored)
python -m career0s.cli import         # load target companies
python -m career0s.cli resolve        # find public ATS feeds (one-off, re-run weekly)
python -m career0s.cli run            # discover -> match -> notes -> report
python -m career0s.cli stats          # see counts
python -m career0s.cli prepare <id>   # open a posting and prep the application
```

Daily, just run `career0s run`. See `scripts/` to schedule it with macOS `launchd`.

## Your private data stays private

Everything personal lives in `_private/` and `data/` — both **gitignored**. Your
CVs, contact details, the target workbook and the SQLite database are never
committed. See [docs/FEASIBILITY.md](docs/FEASIBILITY.md) for what is and isn't
possible for free, and [docs/STRATEGY.md](docs/STRATEGY.md) for the 7-month plan.

## Tech stack (all free)

Python · SQLite · Requests · Playwright · Ollama (`qwen2.5:7b`) · python-docx ·
Obsidian (Markdown) · macOS launchd. No cloud bills, ever.
