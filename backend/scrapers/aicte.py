import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import uuid
import json
import sys
from datetime import datetime

async def _scrape_aicte_async():
    url_target = "https://internship.aicte-india.org/recentlyposted.php"
    internships = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"Navigating to {url_target}...")
            await page.goto(url_target, timeout=60000)
            await page.wait_for_timeout(3000)
            
            for page_index in range(4): # Extract 4 pages (40 internships)
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                for card in soup.find_all('div', class_=lambda c: c and 'card' in c):
                    texts = [t.strip() for t in card.find_all(string=True) if t.strip()]
                    links = [a['href'] for a in card.find_all('a', href=True)]
                    
                    if not texts or len(texts) < 3:
                        continue
                        
                    title = texts[0]
                    company = texts[1]
                    location_or_type = texts[2]
                    
                    # Determine type from location_or_type
                    i_type = "office"
                    if "virtual" in location_or_type.lower() or "online" in location_or_type.lower():
                        i_type = "remote"
                    elif "hybrid" in location_or_type.lower():
                        i_type = "hybrid"
                        
                    stipend = "Unpaid"
                    if "Stipend" in texts:
                        s_idx = texts.index("Stipend")
                        if s_idx + 1 < len(texts):
                            stipend = texts[s_idx + 1]
                            
                    apply_url = links[0] if links else url_target
                    if not apply_url.startswith('http'):
                        apply_url = "https://internship.aicte-india.org/" + apply_url.lstrip('/')
                    
                    # Prevent duplicates just in case
                    if not any(i['applyUrl'] == apply_url and i['role'] == title for i in internships):
                        internships.append({
                            "id": str(uuid.uuid4()),
                            "role": title,
                            "company": company,
                            "type": i_type,
                            "location": location_or_type,
                            "stipend": stipend,
                            "applyUrl": apply_url,
                            "source": "AICTE Internships"
                        })
                
                if page_index < 3:
                    try:
                        next_btn = await page.query_selector("a.page-link:has-text('Next')")
                        if next_btn:
                            await next_btn.click()
                            await page.wait_for_timeout(3000)
                        else:
                            break
                    except:
                        break
                        
        except Exception as e:
            print(f"Error scraping AICTE: {e}")
        finally:
            await browser.close()
            
    return internships

async def scrape_aicte_internships():
    def _run_in_thread():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(_scrape_aicte_async())
    
    return await asyncio.to_thread(_run_in_thread)

if __name__ == "__main__":
    res = asyncio.run(scrape_aicte_internships())
    print(json.dumps(res[:3], indent=2))
    print(f"Total found: {len(res)}")
