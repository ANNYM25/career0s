# 📖 Career0S — The Plain-English Guide

This explains **what Career0S is, how it works, and exactly what to do** — no jargon.
If you read one doc, read this one.

---

## 1. What is it? (in one paragraph)

Career0S is a small program that lives on your Mac. Every day it looks at the
companies you care about, checks their career pages for **new jobs**, keeps only the
ones that **actually fit you**, and hands you a short ranked list. For the jobs you
like, it drafts a cover letter and opens the application form with your details
already filled in — then **stops and lets you press submit yourself**. It costs
**nothing** (no subscriptions, no paid AI, no paid scrapers). It runs on your own
computer.

Think of it as a **research assistant for your job hunt**: it does the boring
searching and form-filling; you do the thinking, the networking, and the final click.

---

## 2. What it does NOT do (on purpose)

- ❌ It **never submits** an application by itself. You always review and click submit.
- ❌ It **never touches LinkedIn** (no auto-connecting, no auto-messaging). That's
  against LinkedIn's rules and can get your account banned. Networking stays 100% you.
- ❌ It **never answers** visa / work-permit / "do you need sponsorship" / declaration
  questions — those are legal statements, so it stops and lets you answer them.

These aren't missing features — they're deliberate guardrails to keep you safe.

---

## 3. How it works (the 5 steps)

```
   YOUR EXCEL            THE INTERNET           THE BRAIN            THE PAPERWORK         YOU
┌──────────────┐     ┌────────────────┐    ┌────────────────┐   ┌─────────────────┐  ┌──────────┐
│ 540 target   │ ──▶ │ checks their   │──▶ │ keeps only the │──▶│ drafts letter + │─▶│ you review│
│ companies    │     │ career pages   │    │ jobs that fit  │   │ fills the form  │  │ & submit  │
└──────────────┘     └────────────────┘    └────────────────┘   └─────────────────┘  └──────────┘
   import              discover               match                prepare              approve
```

1. **Import** — reads your Excel workbook and loads all the companies into a small
   local database.
2. **Discover** — visits the companies' **public job feeds** and pulls down every
   current vacancy (job title, location, description, link).
3. **Match** — scores each job against what you want (sustainable finance / FP&A /
   fintech / etc., entry-level, in Europe, posted recently) and throws away the ones
   that don't fit. An optional local AI double-checks the good ones.
4. **Prepare** — for a job you pick, it writes a cover-letter draft and opens the
   application form with your name/email/phone already typed in and your CV attached.
5. **Approve** — you read everything, answer any personal questions, and submit.

---

## 4. About your Excel file — "do we connect it?"

**It's already connected.** Your workbook
(`Anny_Anish_Expanded_Target_Universe_2026.xlsx`) is in the `data/` folder, and
Career0S reads it automatically.

- If you get an **updated** version of that Excel, just drop the new file into the
  `data/` folder (same name = it replaces the old one). Then run `import` again.
- If you have a **different** Excel, put it in `data/` and run:
  `python -m career0s.cli import --workbook "data/your-file.xlsx"`
- Career0S looks for the sheets named **"Anny Master Targets"** / **"Anny First
  Wave"**. If your file is laid out differently, it will automatically fall back to
  **any sheet that has a "Company" column**.

Your Excel stays **private** — it's never uploaded to GitHub or anywhere.

---

## 5. What to do — step by step (first time)

Open the Terminal app, then copy-paste these one at a time:

```bash
cd ~/Desktop/Outreachforjobs           # go to the project folder
source .venv/bin/activate              # turn the engine on
```

**One-time setup of your details** (so forms can be auto-filled):

```bash
# open these two files and fill in your real info, then save:
open _private/profile.json             # your name, email, phone, LinkedIn, city
open _private/profile_summary.txt      # 5–10 lines about you (for the AI)
```

Also put your 2 CVs in the `_private/` folder (e.g. `_private/CV_Sustainability.pdf`).

**Then run the pipeline:**

```bash
python -m career0s.cli import          # load companies from your Excel
python -m career0s.cli setup-vault     # create your Obsidian "command centre"
python -m career0s.cli resolve         # find which companies have public job feeds (slow, ~5 min; do weekly)
python -m career0s.cli run             # the daily job: discover → match → notes → report
python -m career0s.cli stats           # see the numbers
```

**Every day after that, you only need ONE command:**

```bash
cd ~/Desktop/Outreachforjobs && source .venv/bin/activate && python -m career0s.cli run
```

---

## 6. Where do I see the results?

Two places, both just files on your Mac (open them in **Obsidian** or any text editor):

- **Daily report:** `vault/09_Reports/Daily/<today's date>.md`
  → a ranked table of the best jobs found today, with links.
- **One note per job:** `vault/01_Jobs/`
  → each has the description, why it matched, and a checklist.

To read them nicely: install **Obsidian** (free), and "Open folder as vault" →
choose the `vault` folder. Now your whole job hunt is a tidy dashboard.

---

## 7. Applying to a job

When the report shows a job you like, note its number (id) and run:

```bash
python -m career0s.cli prepare 42 --cv _private/CV_Sustainability.pdf
```

A browser opens on the application page with your details filled in. It will **pause
and tell you** if it spotted visa/declaration questions. You check everything, answer
the personal bits, and **click submit yourself**.

---

## 8. The AI part (free, on your Mac)

Career0S uses **Ollama** with the `qwen2.5:7b` model — a free AI that runs **on your
own computer** (no internet account, no bills). It does two things: double-checks how
well a job fits, and drafts cover letters.

- Make sure Ollama is running (it's already installed). If the AI step is ever
  skipped, the system still works — it just uses the plain rules instead.
- For a *really* important job, you can also paste the job description into ChatGPT or
  Claude yourself for a hand-crafted letter ("Mode B"). That's optional.

---

## 9. Making it run on a schedule (optional)

If you want it to run automatically every morning, see `scripts/com.career0s.daily.plist`
— it uses macOS's built-in scheduler (free). Note: your Mac has to be awake at that
time (a laptop can't run it while shut).

---

## 10. The weekly rhythm (this is what actually gets you the job)

Career0S handles discovery. **You** handle the part that converts:

| Every week | Target |
|------------|--------|
| Quality applications (Career0S preps, you submit) | 10–15 |
| Networking requests (manual, on LinkedIn) | 15–25 |
| Coffee chats / real conversations | 2–3 |
| LinkedIn posts (draft with AI, you publish) | 1–2 |
| Follow-ups | 5–10 |

See `docs/STRATEGY.md` for the full month-by-month plan to June 2027.

---

## 11. Quick troubleshooting

| Problem | Fix |
|---------|-----|
| "No .xlsx found" | Put your Excel in the `data/` folder. |
| "command not found: python" | Run `source .venv/bin/activate` first. |
| AI step is skipped | Start Ollama (open the Ollama app), then re-run. |
| No new jobs found | Re-run `resolve` (feeds change), or most target companies use portals without public feeds — that's expected (see `docs/FEASIBILITY.md`). |
| Form didn't fill much | Fill in `_private/profile.json` with your real details. |

---

## 12. The folders, in one line each

```
career0s/   the program itself (the code)
config/     your settings — which roles/locations you want (anny.yaml)
data/        your Excel + the database  (PRIVATE, never uploaded)
_private/    your CVs, name, email      (PRIVATE, never uploaded)
vault/       your results — reports & job notes (open in Obsidian)
templates/   starter files copied into the vault
docs/        these guides
scripts/     the optional daily scheduler
```

That's it. **Import once, run daily, review the report, apply to the good ones, and
spend the rest of your time networking.** 🎯
