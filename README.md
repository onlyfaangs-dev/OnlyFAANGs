# OnlyFAANGs Scraper

A production-ready job scraper for FAANG + Fortune 500 companies.

## Architecture

Most Fortune 500 companies use one of a handful of ATS (Applicant Tracking System) platforms.
Scraping the platform once covers dozens of companies automatically.

### ATS Platform Coverage
| Platform   | Fortune 500 Companies Using It | Scraper File                        |
|------------|-------------------------------|-------------------------------------|
| Workday    | ~180 companies                | scrapers/workday.py                 |
| Greenhouse | ~60 companies                 | scrapers/greenhouse.py              |
| Lever      | ~40 companies                 | scrapers/lever.py                   |
| iCIMS      | ~50 companies                 | scrapers/icims.py                   |
| Taleo      | ~40 companies                 | scrapers/taleo.py                   |
| Custom     | FAANG + others                | scrapers/custom.py                  |

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in your Supabase credentials
```

## Run

```bash
# Run all scrapers once
python main.py --run-once

# Run on a daily schedule (default: 2am)
python main.py --schedule

# Run a specific scraper only
python main.py --scraper workday
python main.py --scraper greenhouse
python main.py --scraper custom
```

## Output

Jobs are saved to:
- `output/jobs.json` — full flat JSON for your frontend API
- Supabase table `jobs` — if credentials are configured in `.env`

## Notes on Blocking
- Amazon, Apple, Meta use aggressive bot detection — the custom scraper uses Playwright with stealth settings
- Add delays between requests (already configured in utils/http.py)
- Rotate user agents (already configured)
- If a company blocks you, check if they have an official jobs API first (Meta, Google, and LinkedIn do)
