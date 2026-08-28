# scrapers/naukri_scraper.py
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin

def extract_salary(text: str) -> str:
    pattern = r"\₹\d[\d,]*\.?\d*\s*(L|l|LPA|lpa)?(?:\s*[-–]\s*₹?\d[\d,]*\.?\d*\s*(L|l|LPA|lpa)?)?"
    match = re.search(pattern, text)
    return match.group(0) if match else ""

async def scrape_naukri(role: str, location: str, hours: int = 24, max_pages: int = 1):
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        try:
            with open("cookies/naukri_cookies.json", "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Naukri cookies loaded")
        except FileNotFoundError:
            print("⚠️ No cookies found")
        
        page = await context.new_page()
        
        for page_num in range(max_pages):
            # Convert hours to days for Naukri (rounded up)
            days = max(1, int((hours + 23) / 24))
            url = f"https://www.naukri.com/{role.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}?page={page_num + 1}&age={days}"
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
            except Exception as e:
                print(f"Failed to load page: {e}")
                continue
            
            try:
                await page.wait_for_selector("div.jobTuple", timeout=10000)
            except:
                print("No jobs found or page blocked")
                continue
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.jobTuple")
            print(f"Found {len(cards)} jobs on page {page_num + 1}")
            
            for card in cards:
                title_el = card.select_one("a.title")
                company_el = card.select_one("a.subTitle")
                location_el = card.select_one("li.location")
                link_el = card.select_one("a.title")
                
                job_url = ""
                if link_el and link_el.get("href"):
                    job_url = urljoin("https://www.naukri.com", link_el["href"].split("?")[0])
                
                all_text = card.get_text(separator=" ", strip=True)
                
                results.append({
                    "Job Title": title_el.text.strip() if title_el else "",
                    "Company": company_el.text.strip() if company_el else "",
                    "Location": location_el.text.strip() if location_el else "",
                    "Salary Extracted": extract_salary(all_text),
                    "URL": job_url,
                    "Source": "Naukri",
                    "All Text": all_text
                })
        
        await browser.close()
    
    return results