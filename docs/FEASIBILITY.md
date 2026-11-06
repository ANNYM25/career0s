# Feasibility — what's possible for free, what isn't

An honest breakdown of the plan. Green = works today and is built. Amber =
possible with limits. Red = not advisable / not free / against platform terms.

## ✅ Works, free, and built

| Capability | How | Notes |
|------------|-----|-------|
| Import 540 target companies | `openpyxl` on your workbook | Done. |
| Discover vacancies from company feeds | **Greenhouse** & **Lever** public JSON APIs | Unauthenticated, explicitly public, no key. Live-verified: Stripe 764, Databricks 925, Monzo 60, Wise 17 jobs. |
| Auto-detect which companies have a public feed | slug-probe resolver | Guesses board tokens from the company name and probes the API. |
| Deterministic match & score | role-family keywords + seniority gate + location + freshness | Explainable, instant, no AI needed. |
| AI re-rank & reasoning | **Ollama `qwen2.5:7b`** locally | Already installed (4.7 GB). No API bill. Degrades gracefully if off. |
| Cover-letter drafting | local LLM + `python-docx` | Editable `.docx`, free. |
| Obsidian workspace | Markdown files on disk | No subscription; fully private. |
| Daily opportunity report | ranked Markdown | Review in 5 minutes. |
| Application form prep | **Playwright** fills safe fields, attaches CV, then stops | Chromium installed. Never auto-submits. |
| Scheduling | macOS `launchd` / `cron` | Free; no n8n Cloud needed. Mac must be awake. |

## 🟡 Possible, with real limits

| Capability | Reality |
|------------|---------|
| **Workday / SuccessFactors / branded portals** | Most big brands (P&G, Nestlé, banks) use these. No clean public API; each needs a bespoke, brittle collector. Partially doable per-site with Playwright, but high-maintenance. Greenhouse/Lever cover the fintech/scaleup slice cleanly — that's where the resolver pays off. |
| **Auto-filling every application field** | We fill *safe* factual fields and attach a CV. Custom per-company questions, free-text, and screening questions still need you. That's by design. |
| **"Never-touch" scheduling** | A laptop can't guarantee a 24/7 cron. `launchd` runs it whenever the Mac is awake. Truly always-on needs a server (not free). Daily-while-awake is enough for this use case. |
| **ChatGPT inside the code** | Your ChatGPT *subscription* ≠ free OpenAI *API*. The code uses **Ollama** instead (Mode A). For a few high-value roles, paste the JD into ChatGPT manually (Mode B). |
| **Image generation for LinkedIn posts** | No unlimited free API. Use the ChatGPT/Claude UI manually, or local Stable Diffusion if you want it automated. Not built yet. |
| **Buffer free plan** | Free tier allows limited scheduled posts on connected channels. Workable for 1–2 posts/week; LinkedIn's own native scheduler is also free. |

## 🔴 Not advisable / not free / against terms

| Thing | Why we don't |
|-------|--------------|
| **Scraping LinkedIn** (profiles, connections, auto-messages) | Explicitly prohibited; risks account restriction. Networking stays manual. |
| **Auto-submitting applications** | Eligibility/work-authorisation/declarations are legal statements. A bot must not answer them. Hard rule. |
| **Paid scrapers / residential proxies / Firecrawl Cloud** | Costs money. Not used. (Self-hosted ≠ hosted.) |
| **Paid LLM APIs, paid hosting, paid automation (n8n Cloud)** | All avoided; replaced with local/free equivalents. |
| **Mass daily applications (50/day)** | Counter-productive and generic. The strategy targets 10–15 *well-matched* applications/week. |

## Bottom line

The **discovery → matching → prep** core is fully free and working now. The
honest gaps are (1) non-Greenhouse/Lever portals need per-site work, (2) a laptop
isn't a 24/7 server, and (3) networking and final submit stay human — which is
correct, not a limitation.
