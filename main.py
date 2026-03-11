#!/usr/bin/env python3
# main.py
# Entry point for the OnlyFAANGs scraper.
#
# Usage:
#   python main.py --run-once           # scrape everything once now
#   python main.py --schedule           # run daily at 2am
#   python main.py --scraper workday    # run one scraper only
#   python main.py --scraper greenhouse
#   python main.py --scraper lever
#   python main.py --scraper custom

import argparse
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from data.companies import COMPANIES_DEDUPED as COMPANIES
from scrapers.workday import scrape_all_workday
from scrapers.greenhouse import scrape_all_greenhouse
from scrapers.lever import scrape_all_lever
from scrapers.custom import scrape_all_custom
from utils.output import save
from utils.logger import log


def run_all() -> None:
    log.info(f"[Main] Starting full scrape — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    all_jobs = []

    scrapers = [
        ("Greenhouse (Netflix, OpenAI, Stripe…)", scrape_all_greenhouse),
        ("Lever (Reddit, Figma…)",                scrape_all_lever),
        ("Workday (~50 Fortune 500)",             scrape_all_workday),
        ("Custom (FAANG)",                        scrape_all_custom),
    ]

    for name, fn in scrapers:
        log.info(f"[Main] Running: {name}")
        try:
            jobs = fn(COMPANIES)
            log.info(f"[Main] {name}: {len(jobs)} jobs")
            all_jobs.extend(jobs)
        except Exception as e:
            log.error(f"[Main] {name} failed: {e}")

    # Deduplicate by URL
    seen_urls = set()
    deduped = []
    for j in all_jobs:
        if j["url"] not in seen_urls:
            seen_urls.add(j["url"])
            deduped.append(j)

    log.info(f"[Main] Total after dedup: {len(deduped)} jobs (removed {len(all_jobs) - len(deduped)} dupes)")
    save(deduped)
    log.info("[Main] Done.")


def run_scraper(name: str) -> None:
    fn_map = {
        "workday":    scrape_all_workday,
        "greenhouse": scrape_all_greenhouse,
        "lever":      scrape_all_lever,
        "custom":     scrape_all_custom,
    }
    fn = fn_map.get(name)
    if not fn:
        log.error(f"Unknown scraper '{name}'. Choose from: {list(fn_map.keys())}")
        return
    jobs = fn(COMPANIES)
    save(jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OnlyFAANGs job scraper")
    parser.add_argument("--run-once", action="store_true", help="Run all scrapers once and exit")
    parser.add_argument("--schedule", action="store_true", help="Run on daily schedule at 2am")
    parser.add_argument("--scraper", type=str, help="Run a specific scraper: workday|greenhouse|lever|custom")
    args = parser.parse_args()

    if args.scraper:
        run_scraper(args.scraper)
    elif args.schedule:
        import schedule
        import time
        log.info("[Main] Scheduled mode — will run daily at 02:00")
        schedule.every().day.at("02:00").do(run_all)
        run_all()  # Run immediately on start
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_all()
