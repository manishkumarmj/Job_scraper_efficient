# run_posts.py
import asyncio
import pandas as pd
import yaml
import os
import time
from datetime import datetime
from scrapers.linkedin_posts_scraper import scrape_linkedin_posts

def select_location():
    print("\n📍 Select location:")
<<<<<<< HEAD
    print("  1. Delhi NCR (Delhi, Noida, Gurugram, Faridabad)")
=======
    print("  1. Delhi NCR (Delhi, Noida, Greater Noida, Gurugram, Faridabad)")
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    print("  2. Mumbai")
    print("  3. Pune")
    print("  4. Chennai")
    print("  5. Hyderabad")
    print("  6. Bangalore")
    print("  7. Chandigarh / Mohali")
    print("  8. All India (no location filter)")
    print("  9. Custom (enter Geo ID manually)")
    
    location_map = {
<<<<<<< HEAD
        "1": ["102713980", "103644278", "102105104", "106096897"],  # Delhi NCR
        "2": ["102374091"],   # Mumbai
        "3": ["102890884"],   # Pune
        "4": ["103120538"],   # Chennai
        "5": ["103490475"],   # Hyderabad
        "6": ["102844750"],   # Bangalore
        "7": ["103597537"],   # Chandigarh / Mohali
        "8": [],              # All India (no filter)
        "9": "custom"         # Custom
=======
        "1": "102713980,103644278,102105104,106096897",  # Delhi NCR
        "2": "102374091",   # Mumbai
        "3": "102890884",   # Pune
        "4": "103120538",   # Chennai
        "5": "103490475",   # Hyderabad
        "6": "102844750",   # Bangalore
        "7": "103597537",   # Chandigarh / Mohali
        "8": "",            # All India (no filter)
        "9": "custom"       # Custom
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    }
    
    while True:
        choice = input("\nEnter your choice (1-9): ").strip()
        if choice == "9":
            custom = input("Enter Geo ID (comma separated if multiple): ").strip()
<<<<<<< HEAD
            return [g.strip() for g in custom.split(",")] if custom else []
=======
            return custom
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
        if choice in location_map:
            return location_map[choice]
        print("❌ Invalid choice.")

def select_time_filter():
    print("\n📅 Select time filter:")
    print("  1. Last 24 hours")
    print("  2. Last Week")
    options = {"1": "past-24h", "2": "past-week"}
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        if choice in options:
            return options[choice]
        print("❌ Invalid choice.")

def select_content_type():
    print("\n📄 Select content type:")
    print("  1. Jobs")
    print("  2. Posts")
    print("  3. Articles")
    options = {"1": "jobs", "2": "posts", "3": "articles"}
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in options:
            return options[choice]
        print("❌ Invalid choice.")

def select_sort_order():
    print("\n🔽 Select sort order:")
    print("  1. Most Recent Activity (recency)")
    print("  2. Newest First (date_posted)")
    print("  3. Best Match (relevance)")
    options = {"1": "recency", "2": "date_posted", "3": "relevance"}
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in options:
            return options[choice]
        print("❌ Invalid choice.")

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

<<<<<<< HEAD
def generate_urls(keywords, geo_ids, time_filter, content_type, sort_by):
    """Generate all URLs based on selections."""
    sort_map = {
        "recency": "%5B%22recency%22%5D",
        "date_posted": "%5B%22date_posted%22%5D",
        "relevance": "%5B%22relevance%22%5D"
    }
    content_map = {
        "posts": "%5B%22posts%22%5D",
        "jobs": "%5B%22jobs%22%5D",
        "articles": "%5B%22articles%22%5D"
    }
    
    sort_param = sort_map.get(sort_by, "%5B%22recency%22%5D")
    content_param = content_map.get(content_type, "%5B%22posts%22%5D")
    
    location_names = {
        "102713980": "Delhi",
        "103644278": "Noida",
        "102105104": "Gurugram",
        "106096897": "Faridabad",
        "102374091": "Mumbai",
        "102890884": "Pune",
        "103120538": "Chennai",
        "103490475": "Hyderabad",
        "102844750": "Bangalore",
        "103597537": "Chandigarh/Mohali"
    }
    
    url_list = []
    for keyword in keywords:
        if geo_ids:
            for geo_id in geo_ids:
                url = (
                    f"https://www.linkedin.com/search/results/content/"
                    f"?keywords={keyword.replace(' ', '%20')}"
                    f"&origin=FACETED_SEARCH"
                    f"&datePosted=%5B%22{time_filter}%22%5D"
                    f"&contentType={content_param}"
                    f"&sortBy={sort_param}"
                    f"&geoId={geo_id}"
                )
                location_name = location_names.get(geo_id, geo_id)
                url_list.append({
                    "Keyword": keyword,
                    "Location": location_name,
                    "Geo ID": geo_id,
                    "URL": url
                })
        else:
            url = (
                f"https://www.linkedin.com/search/results/content/"
                f"?keywords={keyword.replace(' ', '%20')}"
                f"&origin=FACETED_SEARCH"
                f"&datePosted=%5B%22{time_filter}%22%5D"
                f"&contentType={content_param}"
                f"&sortBy={sort_param}"
            )
            url_list.append({
                "Keyword": keyword,
                "Location": "All India",
                "Geo ID": "",
                "URL": url
            })
    
    return url_list

=======
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
async def main():
    print("\n" + "="*60)
    print("🔍 LINKEDIN POST SCRAPER")
    print("="*60)
    
<<<<<<< HEAD
    geo_ids = select_location()
=======
    geo_id = select_location()
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    time_filter = select_time_filter()
    content_type = select_content_type()
    sort_by = select_sort_order()
    
<<<<<<< HEAD
    # Display location names
    location_names = {
        "102713980": "Delhi",
        "103644278": "Noida",
        "102105104": "Gurugram",
        "106096897": "Faridabad",
=======
    location_names = {
        "102713980,103644278,102105104,106096897": "Delhi NCR",
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
        "102374091": "Mumbai",
        "102890884": "Pune",
        "103120538": "Chennai",
        "103490475": "Hyderabad",
        "102844750": "Bangalore",
<<<<<<< HEAD
        "103597537": "Chandigarh/Mohali"
    }
    
    location_display = "All India"
    if geo_ids:
        loc_names = [location_names.get(g, g) for g in geo_ids]
        location_display = ", ".join(loc_names)
=======
        "103597537": "Chandigarh/Mohali",
        "": "All India"
    }
    location_display = location_names.get(geo_id, geo_id if geo_id else "All India")
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    
    print(f"\n✅ Scraping with:")
    print(f"   📍 Location: {location_display}")
    print(f"   📅 Time: {time_filter}")
    print(f"   📄 Content: {content_type}")
    print(f"   🔽 Sort: {sort_by}")
    print("\n💡 Press Ctrl+C at any time to stop and save partial results.\n")

    with open("inputs_posts.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    keywords = []
    for entry in config:
        kw_list = entry.get("keywords", [])
        if isinstance(kw_list, str):
            kw_list = [kw_list]
        keywords.extend(kw_list)
    
    if not keywords:
        print("❌ No keywords found in inputs_posts.yaml")
        return
    
<<<<<<< HEAD
    # ----- GENERATE AND SAVE ALL URLS -----
    print("📋 Generating all search URLs...")
    url_list = generate_urls(keywords, geo_ids, time_filter, content_type, sort_by)
    
    # Save URLs to Excel
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    url_file = f"results/search_urls_{timestamp}.xlsx"
    df_urls = pd.DataFrame(url_list)
    df_urls.to_excel(url_file, index=False)
    print(f"✅ Saved {len(url_list)} URLs to: {url_file}")
    print("\n📋 Here are your search URLs:\n")
    
    # Print URLs in terminal
    for i, item in enumerate(url_list, 1):
        print(f"{i}. {item['Keyword']} in {item['Location']}")
        print(f"   🔗 {item['URL']}\n")
    
    # Ask user if they want to continue
    continue_choice = input("\n🚀 Do you want to start scraping these URLs? (y/n): ").strip().lower()
    if continue_choice != 'y':
        print("❌ Scraping cancelled. URLs saved to Excel file.")
        return
    
    # Build task list: (keyword, geo_id) for each combination
    tasks = []
    for keyword in keywords:
        if geo_ids:
            for geo_id in geo_ids:
                tasks.append((keyword, geo_id))
        else:
            tasks.append((keyword, ""))
    
    total_tasks = len(tasks)
=======
    print(f"📝 Keywords: {', '.join(keywords)}\n")
    
    total_tasks = len(keywords)
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    all_posts = []
    completed = 0
    start_time = time.time()
    scraped_times = []
    
    try:
<<<<<<< HEAD
        for task_index, (keyword, geo_id) in enumerate(tasks, 1):
            location_name = location_names.get(geo_id, geo_id if geo_id else "All India")
            print(f"\n{'='*60}")
            print(f"📍 Search {task_index}/{total_tasks}: '{keyword}' in '{location_name}'")
=======
        for task_index, keyword in enumerate(keywords, 1):
            print(f"\n{'='*60}")
            print(f"📍 Search {task_index}/{total_tasks}: '{keyword}'")
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
            print(f"{'='*60}")
            
            task_start = time.time()
            
            posts = await scrape_linkedin_posts(
                keyword=keyword,
                geo_id=geo_id,
                time_filter=time_filter,
                content_type=content_type,
                sort_by=sort_by,
                max_posts=50
            )
            all_posts.extend(posts)
            
            task_duration = time.time() - task_start
            scraped_times.append(task_duration)
            completed += 1
            
            avg_time = sum(scraped_times) / len(scraped_times)
            remaining = total_tasks - completed
            eta_seconds = avg_time * remaining
            
<<<<<<< HEAD
            print(f"\n   ✅ Found {len(posts)} posts for '{keyword}' in '{location_name}'")
            print(f"   📊 Progress: {completed}/{total_tasks} searches done")
=======
            print(f"\n   ✅ Found {len(posts)} posts for '{keyword}'")
            print(f"   📊 Progress: {completed}/{total_tasks} keywords done")
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
            if remaining > 0:
                print(f"   ⏳ ETA: {format_time(eta_seconds)} remaining (avg {format_time(avg_time)} per search)")
            else:
                print("   🎯 All searches completed!")
            
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping stopped by user. Saving partial results...")
    
    if not all_posts:
        print("No posts found.")
        return
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_posts = []
    for post in all_posts:
        url = post.get("URL", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_posts.append(post)
        elif not url:
            unique_posts.append(post)
    
    duplicate_count = len(all_posts) - len(unique_posts)
    if duplicate_count > 0:
        print(f"\n🔹 Removed {duplicate_count} duplicate post(s)")
    
<<<<<<< HEAD
    # Save results
    df = pd.DataFrame(unique_posts)
=======
    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(unique_posts)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    time_label = time_filter.replace("past-", "")
    output_file = f"results/posts_{time_label}_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Saved {len(df)} posts to {output_file}")
<<<<<<< HEAD
    print(f"✅ URLs saved to: {url_file}")
=======
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())