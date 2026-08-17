import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import random
import re

def extract_salary(text: str) -> str:
    pattern = r"\$\d[\d,]*\.?\d*\s*(k|K|m|M)?(?:\s*[-–]\s*\$?\d[\d,]*\.?\d*\s*(k|K|m|M)?)?(?:\s*/\s*(hr|hour|year))?"
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def extract_experience(text: str) -> str:
    if not text:
        return ""
    patterns = [
        r"(Entry\s*level|Mid-Senior\s*level|Senior\s*level|Associate|Internship|Fresher)",
        r"(\d+\s*[-–]\s*\d+\s*(?:year|yr|yrs|years?))",
        r"(\d+\s*\+\s*(?:year|yr|yrs|years?))",
        r"(\d+\s*(?:year|yr|yrs|years?))",
        r"(?:minimum|at least|min\.?|max\.?)\s*(\d+\s*(?:year|yr|yrs|years?))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""

async def human_like_scroll(page, times=3):
    for _ in range(times):
        await page.mouse.wheel(0, 2500)
        await asyncio.sleep(random.uniform(2, 4))

async def scrape_job_detail(browser, job_url):
    salary, all_text, experience = "", "", ""
    try:
        page = await browser.new_page()
        await page.goto(job_url, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))
        await human_like_scroll(page, times=2)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        desc_el = soup.select_one("div.show-more-less-html__markup")
        if desc_el:
            all_text = desc_el.get_text(separator=" ", strip=True)
            salary = extract_salary(all_text)
        # Structured experience
        exp_labels = soup.find_all("span", string=re.compile("Experience", re.I))
        for label in exp_labels:
            parent = label.find_parent()
            if parent:
                value_el = parent.select_one("span.job-criteria__text")
                if value_el:
                    experience = value_el.get_text(strip=True)
                    break
        if not experience:
            exp_items = soup.select("li.job-criteria__item")
            for item in exp_items:
                label = item.select_one("span.job-criteria__label")
                if label and "experience" in label.get_text().lower():
                    value = item.select_one("span.job-criteria__text")
                    if value:
                        experience = value.get_text(strip=True)
                        break
        if not experience and all_text:
            experience = extract_experience(all_text)
        await page.close()
    except Exception as e:
        print(f"⚠️ Failed to scrape {job_url}: {e}")
    return salary, all_text, experience

async def scrape_linkedin(
    role: str,
    location: str,
    hours: int = 24,
    max_jobs: int = 50,
    fresher_filter_url: bool = False
):
    results = []
    semaphore = asyncio.Semaphore(3)

    time_map = {
        1: "r3600",
        3: "r10800",
        6: "r21600",
        9: "r32400",
        12: "r43200",
        15: "r54000",
        24: "r86400",
    }
    time_param = time_map.get(hours, "r86400")

    # Use persistent profile (no login prompts)
    user_data_dir = "./linkedin_profile"

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=200
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()

        url = f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_TPR={time_param}"
        if fresher_filter_url:
            url += "&f_E=1,2,3"

        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(4, 7))

        # --- NO LOGIN CHECKS, NO PROMPTS ---
        # Just scroll and scrape.

        await human_like_scroll(page, times=4)

        all_cards = await page.query_selector_all(
            "li.jobs-search-results__list-item, ul.jobs-search__results-list li, div.job-card-container"
        )

        # Filter sponsored
        organic_cards = []
        for card in all_cards:
            is_sponsored = False
            sponsored_badge = await card.query_selector("span:has-text('Sponsored'), .sponsored-badge, [data-testid='sponsored']")
            if sponsored_badge:
                is_sponsored = True
            else:
                text_content = await card.inner_text() if card else ""
                if "sponsored" in text_content.lower():
                    is_sponsored = True
            if not is_sponsored:
                organic_cards.append(card)

        print(f"✅ Found {len(organic_cards)} organic LinkedIn job cards (skipped {len(all_cards) - len(organic_cards)} sponsored)")
        cards = organic_cards[:max_jobs]

        job_entries = []
        for card in cards:
            title_el = await card.query_selector("h3.base-search-card__title, a.job-card-container__link")
            company_el = await card.query_selector("h4.base-search-card__subtitle, a.job-card-container__company-name")
            location_el = await card.query_selector("span.job-search-card__location, span.job-card-container__location")
            link_el = await card.query_selector("a.base-card__full-link, a.job-card-container__link")

            job_url = ""
            if link_el:
                job_url = await link_el.get_attribute("href")
                if job_url:
                    job_url = urljoin("https://www.linkedin.com", job_url.split("?")[0])

            job_entries.append({
                "Job Title": (await title_el.inner_text()).strip() if title_el else "",
                "Company": (await company_el.inner_text()).strip() if company_el else "",
                "Location": (await location_el.inner_text()).strip() if location_el else "",
                "Experience Required": "",
                "Salary Extracted": "",
                "All Text": "",
                "URL": job_url,
                "Source": "LinkedIn"
            })

        async def fetch_details(job):
            if job["URL"]:
                async with semaphore:
                    salary, all_text, experience = await scrape_job_detail(browser, job["URL"])
                    job["Salary Extracted"] = salary
                    job["All Text"] = all_text
                    job["Experience Required"] = experience
            return job

        tasks = [fetch_details(job) for job in job_entries]
        results = await asyncio.gather(*tasks)

        await browser.close()

    return results