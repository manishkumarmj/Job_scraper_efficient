# run_naukri.py
import asyncio
import pandas as pd
import yaml
import os
from datetime import datetime
from error_run_in.naukri_scraper import scrape_naukri

def select_hours():
    print("\n📅 Select time range for jobs:")
    print("  1. Last 1 hour")
    print("  2. Last 3 hours")
    print("  3. Last 6 hours")
    print("  4. Last 9 hours")
    print("  5. Last 12 hours")
    print("  6. Last 15 hours")
    print("  7. Last 24 hours")
    
    options = {
        "1": 1,
        "2": 3,
        "3": 6,
        "4": 9,
        "5": 12,
        "6": 15,
        "7": 24
    }
    
    while True:
        choice = input("\nEnter your choice (1-7): ").strip()
        if choice in options:
            return options[choice]
        print("❌ Invalid choice. Please enter 1-7.")

async def main():
    hours = select_hours()
    print(f"\n✅ Scraping jobs from last {hours} hours\n")
    
    with open("inputs.yaml", "r") as f:
        inputs = yaml.safe_load(f)

    all_jobs = []
    for entry in inputs:
        role = entry["role"]
        for location in entry["locations"]:
            print(f"Scraping Naukri for {role} in {location}...")
            jobs = await scrape_naukri(role, location, hours=hours, max_pages=1)
            all_jobs.extend(jobs)

    if not all_jobs:
        print("No jobs found")
        return

    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(all_jobs)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"results/naukri_{hours}h_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved {len(df)} jobs to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())