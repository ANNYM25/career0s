<div align="center">

# 🎯 Career0S

### An open-source, **zero-cost** career-acquisition system

*Find the right jobs automatically. Keep every submission in human hands.*

![Cost](https://img.shields.io/badge/cost-%E2%82%AC0-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Local LLM](https://img.shields.io/badge/AI-Ollama%20(local)-000000?style=for-the-badge)
![Playwright](https://img.shields.io/badge/automation-Playwright-2EAD33?style=for-the-badge&logo=playwright)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

</div>

---

Career0S turns a list of target companies into a **daily pipeline of matched job
opportunities**, drafts the paperwork, and prepares applications for you — while
keeping **every submission under your control**. It runs entirely on your own Mac
with **no paid APIs, no paid hosting, no paid scrapers**. Total cost: **€0**.

Built for a 7-month run toward **June 2027**, focused on **Sustainable Finance /
FinTech** early-career roles across Europe.

```
┌───────────────┐   ┌───────────────┐   ┌──────────────────┐   ┌─────────────────┐   ┌──────────────┐
│ Target        │──▶│ Job discovery │──▶│ Matching &       │──▶│ Application     │──▶│ 🧑 YOUR      │
│ universe      │   │ public ATS    │   │ scoring          │   │ preparation     │   │ approval     │
│ (your Excel)  │   │ APIs (free)   │   │ rules + local AI │   │ letter + form   │   │ review+submit│
└───────────────┘   └───────────────┘   └──────────────────┘   └─────────────────┘   └──────────────┘
```

## ✨ What it does

| Stage | How | Cost |
|-------|-----|:----:|
| 📥 Import target companies | `openpyxl` reads your workbook | €0 |
| 🔎 Find companies with public job feeds | probe Greenhouse / Lever public APIs | €0 |
| 🛰️ Discover vacancies daily | public ATS JSON APIs (no LinkedIn scraping) | €0 |
| 🎯 Score & shortlist | deterministic rules + optional local LLM (Ollama) | €0 |
| 🗂️ Write per-job notes | Markdown into an Obsidian vault | €0 |
| 📊 Daily opportunity report | ranked shortlist Markdown | €0 |
| ✍️ Draft cover letters | `python-docx` + local LLM | €0 |
| 🤖 Prepare applications | Playwright fills safe fields, **stops for you to submit** | €0 |

## 🔒 The golden rule

> **No application is ever submitted automatically.**

Career0S fills the safe, factual fields (name, email, phone), attaches one of your
two CVs, drafts the cover letter, then **stops**. Eligibility, work-authorisation,
declarations and CAPTCHAs always halt the automation for your review.

It also **does not** scrape or automate LinkedIn (profiles, connections, messages)
— that's against their terms and risks your account. **Networking stays human; only
discovery is automated.**

## 🚀 Quick start

```bash
# 1. Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# 2. Add your data (gitignored, never committed)
#    - put the workbook at  data/<workbook>.xlsx
#    - cp config/profile.example.json         _private/profile.json       # then fill in
#    - cp config/profile_summary.example.txt  _private/profile_summary.txt # then fill in

# 3. Run
python -m career0s.cli import         # load target companies
python -m career0s.cli setup-vault    # create the Obsidian command-centre
python -m career0s.cli resolve        # find public ATS feeds (re-run weekly)
python -m career0s.cli run            # discover → match → notes → report
python -m career0s.cli stats          # see counts
python -m career0s.cli prepare <id>   # open a posting & prep the application
```

Daily, just run `career0s run`. See [`scripts/`](scripts/) to schedule it with macOS `launchd`.

## 🧱 Architecture

```
career0s/
├── importer.py        # Excel → SQLite
├── resolver.py        # company name → public ATS board token (slug probe)
├── collectors/        # Greenhouse, Lever … (public APIs; add more here)
├── matching.py        # deterministic scoring + seniority/location gates
├── llm.py             # Ollama wrapper (match re-rank + cover letters)
├── obsidian.py        # per-job Markdown records
├── report.py          # daily opportunity report
├── documents.py       # cover-letter .docx (python-docx)
├── apply.py           # Playwright prep — fills safe fields, STOPS for review
└── cli.py             # the command-line entry point
config/   templates/   docs/   scripts/   vault/
```

## 📚 Docs

- [**docs/STRATEGY.md**](docs/STRATEGY.md) — the 7-month plan (Nov 2026 → June 2027), weekly targets, role families.
- [**docs/FEASIBILITY.md**](docs/FEASIBILITY.md) — an honest breakdown of what's possible for free, what has limits, and what to avoid.

## 🔐 Your private data stays private

Everything personal lives in `_private/` and `data/` — **both gitignored**. Your
CVs, contact details, the target workbook and the SQLite database are **never
committed**. Only code, docs and empty templates are tracked.

## 🧰 Tech stack (all free)

Python · SQLite · Requests · Playwright · Ollama (`qwen2.5:7b`) · python-docx ·
Obsidian (Markdown) · macOS `launchd`. No cloud bills, ever.

---

<div align="center">
<sub>Built with Claude Code · MIT License · Not affiliated with any employer or ATS provider.</sub>
</div>
