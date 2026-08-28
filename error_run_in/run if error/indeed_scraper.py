import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin

def extract_salary(text: str) -> str:
    pattern = r"\$\d[\d,]*\.?\d*\s*(k|K|m|M)?(?:\s*[-–]\s*\$?\d[\d,]*\.?\d*\s*(k|K|m|M)?)?(?:\s*/\s*(hr|hour|year))?"
    match = re.search(pattern, text)
    return match.group(0) if match else ""

async def scrape_indeed(role: str, location: str, hours: int = 24, max_pages: int = 1):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        
        try:
            with open("cookies/indeed_cookies.json", "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Indeed cookies loaded")
        except FileNotFoundError:
            print("⚠️ No cookies found")
        
        page = await context.new_page()

        for page_num in range(max_pages):
            start = page_num * 10
            url = (
                f"https://www.indeed.com/jobs?"
                f"q={role.replace(' ', '+')}&l={location.replace(' ', '+')}&fromage={hours}&start={start}"
            )
            await page.goto(url)

            try:
                await page.wait_for_selector("div.job_seen_beacon", timeout=10000)
            except:
                print("⚠️ Timeout waiting for job cards")
                continue

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.job_seen_beacon")
            print(f"Found {len(cards)} job cards on page {page_num + 1}")

            for card in cards:
                title_el = card.select_one("h2.jobTitle span")
                company_el = card.select_one("span[data-testid='company-name']")
                location_el = card.select_one("div[data-testid='text-location']")
                link_el = card.select_one("a.jcs-JobTitle")
                all_text = card.get_text(separator=" ", strip=True)

                job_url = ""
                if link_el and link_el.get("href"):
                    job_url = urljoin("https://www.indeed.com", link_el["href"].split("?")[0])

                results.append({
                    "Job Title": title_el.text.strip() if title_el else "",
                    "Company": company_el.text.strip() if company_el else "",
                    "Location": location_el.text.strip() if location_el else "",
                    "Salary Extracted": extract_salary(all_text),
                    "URL": job_url,
                    "Source": "Indeed",
                    "All Text": all_text
                })

        await browser.close()
    return results