# run_linkedin.py
import asyncio
import pandas as pd
import yaml
import os
from datetime import datetime
from scrapers.linkedin_scraper import scrape_linkedin

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
        "1": 1, "2": 3, "3": 6, "4": 9,
        "5": 12, "6": 15, "7": 24
    }
    while True:
        choice = input("\nEnter your choice (1-7): ").strip()
        if choice in options:
            return options[choice]
        print("❌ Invalid choice.")

def select_filter_mode():
    print("\n🔍 Fresher job filter options:")
    print("  1. No filter (scrape all jobs)")
    print("  2. Use LinkedIn's built-in experience filter (Internship, Entry, Associate)")
    print("  3. Scrape all, then filter fresher jobs after scraping (recommended for freshers)")
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return int(choice)
        print("❌ Invalid choice.")

def is_fresher_job(job):
    """
    Smarter fresher detection.
    - If experience text is empty -> KEEP (can't judge, so don't discard)
    - If senior keywords appear -> DISCARD (unless entry/associate also appear)
    - If fresher keywords appear -> KEEP
    """
    exp = job.get("Experience Required", "").lower()
    
    # If no experience info, keep it (don't discard)
    if not exp or exp == "":
        return True
    
    # Senior keywords (red flags)
    senior_keywords = ["senior", "lead", "manager", "director", "executive", "principal", "staff", "head"]
    
    # Fresher keywords (green flags)
    fresher_keywords = ["entry", "fresher", "internship", "intern", "trainee", "associate", 
                        "0-", "1-", "2-", "0 year", "1 year", "2 year", 
                        "less than", "no experience", "fresher"]
    
    # Check for senior keywords
    has_senior = any(kw in exp for kw in senior_keywords)
    has_fresher = any(kw in exp for kw in fresher_keywords)
    
    # If both appear, fresher wins (e.g., "Entry level - Senior" – keep)
    if has_fresher:
        return True
    
    # If only senior appears, discard
    if has_senior:
        return False
    
    # If neither appears, keep (safe default)
    return True

async def main():
    hours = select_hours()
    filter_mode = select_filter_mode()
    
    print(f"\n✅ Scraping jobs from last {hours} hours")
    if filter_mode == 2:
        print("   🔹 Using LinkedIn's built-in fresher filter (fastest)")
    elif filter_mode == 3:
        print("   🔹 Scraping all jobs, then filtering fresher-friendly ones (most accurate)")
    else:
        print("   🔹 No filter – scraping all jobs")
    print()

    with open("inputs.yaml", "r") as f:
        inputs = yaml.safe_load(f)

    all_jobs = []
    for entry in inputs:
        role = entry["role"]
        for location in entry["locations"]:
            print(f"Scraping LinkedIn for {role} in {location}...")
            jobs = await scrape_linkedin(
                role, location,
                hours=hours,
                max_jobs=50,
                fresher_filter_url=(filter_mode == 2)  # Only mode 2 uses URL filter
            )
            all_jobs.extend(jobs)

    if not all_jobs:
        print("No jobs found")
        return

    # Apply post-scrape filtering ONLY for mode 2 and 3
    if filter_mode in (2, 3):
        original_count = len(all_jobs)
        all_jobs = [job for job in all_jobs if is_fresher_job(job)]
        print(f"\n🔹 Post-filter: kept {len(all_jobs)} fresher-friendly jobs out of {original_count} total")

    if not all_jobs:
        print("No fresher-friendly jobs found.")
        return

    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(all_jobs)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"results/linkedin_{hours}h_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved {len(df)} jobs to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())