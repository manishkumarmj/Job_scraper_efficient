# main.py
import pandas as pd
import asyncio
import yaml
import os
from datetime import datetime

from scrapers.linkedin_scraper import scrape_linkedin
from scrapers.indeed_scraper import scrape_indeed

async def main():
    # Load YAML inputs
    with open("inputs.yaml", "r") as f:
        inputs = yaml.safe_load(f)

    all_jobs = []

    for entry in inputs:
        role = entry["role"]
        for location in entry["locations"]:
            print(f"Scraping LinkedIn for {role} jobs in {location} (last 24h)...")
            linkedin_jobs = await scrape_linkedin(role, location)
            all_jobs.extend(linkedin_jobs)  # LinkedIn first

            print(f"Scraping Indeed for {role} jobs in {location}...")
            indeed_jobs = await scrape_indeed(role, location, max_pages=1)
            all_jobs.extend(indeed_jobs)  # Indeed after LinkedIn

    if not all_jobs:
        print("⚠️ No jobs found for any roles/locations.")
        return

    # Combined sources for filename
    scraper_sources = set(job["Source"] for job in all_jobs)
    source_str = "_".join(sorted(scraper_sources))

    # Ensure results folder exists
    os.makedirs("results", exist_ok=True)

    df = pd.DataFrame(all_jobs)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    role_sanitized = role.replace(" ", "_")
    output_file = f"results/{role_sanitized}_{timestamp}_{source_str}_jobs.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved {len(df)} jobs to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
