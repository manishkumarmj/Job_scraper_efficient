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
        
<<<<<<< HEAD
        # Build URL with origin parameter
        url = (
            f"https://www.linkedin.com/search/results/content/"
            f"?keywords={keyword.replace(' ', '%20')}"
            f"&origin=FACETED_SEARCH"
=======
        # Build URL with optional geo_id
        url = (
            f"https://www.linkedin.com/search/results/content/"
            f"?keywords={keyword.replace(' ', '%20')}"
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
            f"&datePosted=%5B%22{time_filter}%22%5D"
            f"&contentType={content_param}"
            f"&sortBy={sort_param}"
        )
        if geo_id:
            url += f"&geoId={geo_id}"
        
<<<<<<< HEAD
        print(f"\n🔗 URL: {url}")
        print(f"📋 Copy this URL and paste in browser to verify\n")
        
        # FIX: Use 'domcontentloaded' instead of 'networkidle'
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(random.uniform(4, 6))
        
        await human_like_scroll(page, times=5)
        
        # Wait for ANY link (posts always have links)
        try:
            await page.wait_for_selector("a", timeout=15000)
            print("✅ Page loaded – found links")
        except:
            print("⚠️ Page loaded but no links found")
            await browser.close()
            return results
        
        # Find ALL containers that might be posts
        containers = await page.query_selector_all(
            "div[data-urn], "
            "li, "
            "div.feed-shared-update-v2, "
            "div.occludable-update, "
            "div.search-result, "
            "div.search-result__occludable-update"
        )
        
        # Filter: only keep containers that have an <a> tag inside
        post_containers = []
        for container in containers:
            link = await container.query_selector("a")
            if link:
                post_containers.append(container)
        
        print(f"✅ Found {len(post_containers)} post containers for '{keyword}'")
        posts = post_containers[:max_posts]
        
        for post in posts:
            # Get post URL
            link_el = await post.query_selector("a")
=======
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
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
            post_url = ""
            if link_el:
                post_url = await link_el.get_attribute("href")
                if post_url:
                    post_url = urljoin("https://www.linkedin.com", post_url.split("?")[0])
            
<<<<<<< HEAD
            # Get all text from container (fallback)
            full_text = await post.inner_text() if post else ""
            
            # Try specific selectors for text
            text_el = (
                await post.query_selector("div.feed-shared-update-v2__description") or
                await post.query_selector("div.break-words") or
                await post.query_selector("div.search-result__snippets")
            )
            text = await text_el.inner_text() if text_el else full_text
            
            # Get author
            author_el = (
                await post.query_selector("span.feed-shared-actor__name") or
                await post.query_selector("span.search-result__actor-name")
            )
            author = await author_el.inner_text() if author_el else ""
            
            # Fallback: extract author from first line
            if not author and full_text:
                lines = full_text.split('\n')
                if lines:
                    author = lines[0].strip()
            
            # Get author title
            title_el = (
                await post.query_selector("span.feed-shared-actor__title") or
                await post.query_selector("span.search-result__actor-title")
            )
            author_title = await title_el.inner_text() if title_el else ""
            
            # Get likes
            likes_el = await post.query_selector("span.social-details-social-counts__reaction-count")
            likes = await likes_el.inner_text() if likes_el else "0"
            
            # Get comments
=======
            text_el = await post.query_selector("div.feed-shared-update-v2__description, div.break-words")
            text = await text_el.inner_text() if text_el else ""
            
            author_el = await post.query_selector("span.feed-shared-actor__name")
            author = await author_el.inner_text() if author_el else ""
            
            title_el = await post.query_selector("span.feed-shared-actor__title")
            author_title = await title_el.inner_text() if title_el else ""
            
            likes_el = await post.query_selector("span.social-details-social-counts__reaction-count")
            likes = await likes_el.inner_text() if likes_el else "0"
            
>>>>>>> 1f28a5fee1f74672dff0c012bd734be9074a6ea6
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