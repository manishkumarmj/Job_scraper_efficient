import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import random

async def human_like_scroll(page, times=3):
    for _ in range(times):
        await page.mouse.wheel(0, 2500)
        await asyncio.sleep(random.uniform(2, 4))

async def scrape_linkedin_posts(
    keyword: str,
    geo_id: str = "",
    time_filter: str = "past-24h",
    content_type: str = "posts",
    sort_by: str = "recency",
    max_posts: int = 50
):
    results = []
    
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
    
    user_data_dir = "./linkedin_profile"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=300
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Build URL with optional geo_id
        url = (
            f"https://www.linkedin.com/search/results/content/"
            f"?keywords={keyword.replace(' ', '%20')}"
            f"&datePosted=%5B%22{time_filter}%22%5D"
            f"&contentType={content_param}"
            f"&sortBy={sort_param}"
        )
        if geo_id:
            url += f"&geoId={geo_id}"
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(6, 9))
        
        await human_like_scroll(page, times=5)
        
        try:
            await page.wait_for_selector("div.feed-shared-update-v2, div.occludable-update", timeout=15000)
        except:
            print("⚠️ No posts found or page took too long")
            await browser.close()
            return results
        
        all_posts = await page.query_selector_all(
            "div.feed-shared-update-v2, div.occludable-update"
        )
        
        print(f"✅ Found {len(all_posts)} posts for '{keyword}'")
        posts = all_posts[:max_posts]
        
        for post in posts:
            link_el = await post.query_selector("a.app-aware-link")
            post_url = ""
            if link_el:
                post_url = await link_el.get_attribute("href")
                if post_url:
                    post_url = urljoin("https://www.linkedin.com", post_url.split("?")[0])
            
            text_el = await post.query_selector("div.feed-shared-update-v2__description, div.break-words")
            text = await text_el.inner_text() if text_el else ""
            
            author_el = await post.query_selector("span.feed-shared-actor__name")
            author = await author_el.inner_text() if author_el else ""
            
            title_el = await post.query_selector("span.feed-shared-actor__title")
            author_title = await title_el.inner_text() if title_el else ""
            
            likes_el = await post.query_selector("span.social-details-social-counts__reaction-count")
            likes = await likes_el.inner_text() if likes_el else "0"
            
            comments_el = await post.query_selector("span.social-details-social-counts__comments")
            comments = await comments_el.inner_text() if comments_el else "0"
            
            results.append({
                "Keyword": keyword,
                "Location": geo_id,
                "Post Text": text.strip(),
                "Author": author.strip(),
                "Author Title": author_title.strip(),
                "Likes": likes.strip(),
                "Comments": comments.strip(),
                "URL": post_url,
                "Source": "LinkedIn"
            })
        
        await browser.close()
    
    return results