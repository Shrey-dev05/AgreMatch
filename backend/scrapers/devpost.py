import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import uuid
from datetime import datetime

import sys

async def _scrape_devpost_async():
    hackathons = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to devpost...")
            await page.goto("https://devpost.com/hackathons", timeout=60000)
            
            # Wait for content
            await page.wait_for_timeout(3000) # Simple wait to ensure JS loaded
            
            html = await page.content()
            with open("devpost_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Selectors based on Devpost's current DOM (their list is a bunch of articles or divs)
            tiles = soup.select(".hackathon-tile")
            
            for tile in tiles[:24]:
                title_elem = tile.select_one("h3")
                title = title_elem.text.strip() if title_elem else "Unknown Hackathon"
                
                url_elem = tile.select_one("a.tile-anchor") or tile.select_one("a[href]")
                url = url_elem['href'] if url_elem else "https://devpost.com"
                
                if url.startswith("//"): url = "https:" + url
                if url.startswith("/"): url = "https://devpost.com" + url
                
                theme_elems = tile.select(".theme-label")
                theme = ", ".join([t.text.strip() for t in theme_elems]) if theme_elems else "Open Theme"
                
                # Try finding prize
                prize_pool = 0
                prize_elem = tile.select_one(".prize-amount") 
                if prize_elem:
                    num_str = ''.join(filter(str.isdigit, prize_elem.text))
                    if num_str:
                        prize_pool = int(num_str)
                
                h_type = "virtual"
                loc_elem = tile.select_one(".info .location")
                if loc_elem and "Online" not in loc_elem.text and "Anywhere" not in loc_elem.text:
                    h_type = "in-person"
                    
                date_str = datetime.utcnow().isoformat() + "Z"
                date_elem = tile.select_one(".submission-period")
                if date_elem:
                    date_str = date_elem.text.strip()
                    
                hackathons.append({
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "organization": "Devpost", 
                    "type": h_type,
                    "theme": theme,
                    "prizePool": prize_pool,
                    "startDate": date_str,
                    "endDate": date_str,
                    "applyUrl": url,
                    "source": "Devpost",
                })
        except Exception as e:
            print(f"Error scraping devpost: {e}")
        finally:
            await browser.close()
            
    return hackathons

async def scrape_devpost_hackathons():
    # Runs the async scraper in a cleanly isolated thread with ProactorEventLoop on Windows.
    def _run_in_thread():
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(_scrape_devpost_async())
    
    return await asyncio.to_thread(_run_in_thread)

import json
if __name__ == "__main__":
    res = asyncio.run(scrape_devpost_hackathons())
    for r in res[:3]:
        print(json.dumps(r, indent=2))
    print(f"Total found: {len(res)}")
