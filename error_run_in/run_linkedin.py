# run_linkedin.py
import asyncio
import pandas as pd
import yaml
import os
import time
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
    exp = job.get("Experience Required", "").lower()
    if not exp or exp == "":
        return True
    senior_keywords = ["senior", "lead", "manager", "director", "executive", "principal", "staff", "head"]
    fresher_keywords = ["entry", "fresher", "internship", "intern", "trainee", "associate",
                        "0-", "1-", "2-", "0 year", "1 year", "2 year",
                        "less than", "no experience"]
    has_senior = any(kw in exp for kw in senior_keywords)
    has_fresher = any(kw in exp for kw in fresher_keywords)
    if has_fresher:
        return True
    if has_senior:
        return False
    return True

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

async def main():
    hours = select_hours()
    filter_mode = select_filter_mode()
    
    print(f"\n✅ Scraping jobs from last {hours} hours")
    mode_desc = {
        1: "No filter – scraping all jobs",
        2: "Using LinkedIn's built-in fresher filter (fastest)",
        3: "Scraping all jobs, then filtering fresher-friendly ones (most accurate)"
    }
    print(f"   🔹 {mode_desc[filter_mode]}")
    print("\n💡 Press Ctrl+C at any time to stop and save partial results.\n")

    with open("inputs.yaml", "r") as f:
        inputs = yaml.safe_load(f)

    # Build task list: (role, location) for each combination
    tasks = []
    for entry in inputs:
        roles = entry["role"]
        if isinstance(roles, str):
            roles = [roles]
        for role in roles:
            for location in entry["locations"]:
                tasks.append((role, location))

    total_tasks = len(tasks)
    all_jobs = []
    completed = 0
    start_time = time.time()
    scraped_times = []

    try:
        for role, location in tasks:
            print(f"\n🔍 Scraping LinkedIn for '{role}' in '{location}'...")
            task_start = time.time()

            jobs = await scrape_linkedin(
                role, location,
                hours=hours,
                max_jobs=50,
                fresher_filter_url=(filter_mode == 2)
            )
            all_jobs.extend(jobs)

            task_duration = time.time() - task_start
            scraped_times.append(task_duration)
            completed += 1

            avg_time = sum(scraped_times) / len(scraped_times)
            remaining = total_tasks - completed
            eta_seconds = avg_time * remaining
            elapsed = time.time() - start_time

            print(f"   ✅ Found {len(jobs)} jobs (completed {completed}/{total_tasks})")
            if remaining > 0:
                print(f"   ⏳ ETA: {format_time(eta_seconds)} remaining (avg {format_time(avg_time)} per search)")
            else:
                print("   🎯 All searches completed!")

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️  Scraping stopped by user. Saving partial results...")

    if not all_jobs:
        print("No jobs found.")
        return

    # Apply post-scrape filtering for mode 2 & 3
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