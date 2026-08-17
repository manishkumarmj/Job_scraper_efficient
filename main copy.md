# main.py
import pandas as pd
import asyncio
from scrapers.indeed_scraper import scrape_indeed
import yaml
import os
from datetime import datetime

async def main():
    # Load YAML inputs
    with open("inputs.yaml", "r") as f:
        inputs = yaml.safe_load(f)

    all_jobs = []

    for entry in inputs:
        role = entry["role"]
        for location in entry["locations"]:
            print(f"Scraping Indeed for {role} jobs in {location}...")
            jobs = await scrape_indeed(role, location, max_pages=1)
            all_jobs.extend(jobs)

    if not all_jobs:
        print("⚠️ No jobs found for any roles/locations.")
        return

    scraper_source = all_jobs[0]["Source"] if all_jobs else "jobs"

    # Ensure results folder exists
    os.makedirs("results", exist_ok=True)

    df = pd.DataFrame(all_jobs)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    role_sanitized = role.replace(" ", "_")  # avoid spaces in filename
    output_file = f"results/{role_sanitized}_{timestamp}_{scraper_source}_jobs.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved {len(df)} jobs to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
