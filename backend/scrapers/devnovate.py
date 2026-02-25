import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import uuid
import json
import sys
import re
from datetime import datetime

async def _scrape_devnovate_async():
    url_target = "https://devnovate.co/events"
    hackathons = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"Navigating to {url_target}...")
            await page.goto(url_target, timeout=60000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            cards = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/event/' in href.lower() or '/hackathon/' in href.lower():
                    container = a.find_parent('div', class_=lambda c: c and 'group' in c) or a.find_parent('div', class_=lambda c: c and 'flex-col' in c and 'shadow' in c)
                    if container and container not in cards:
                        cards.add(container)
                        title_elem = container.find(['h2', 'h3', 'h4'])
                        if not title_elem: continue
                        title = title_elem.text.strip()
                        
                        text_blocks = container.find_all(string=True)
                        text_list = [t.strip() for t in text_blocks if t.strip()]
                        
                        # Parse type
                        h_type = 'virtual'
                        if 'OFFLINE' in text_list: h_type = 'in-person'
                        elif 'HYBRID' in text_list: h_type = 'hybrid'
                        
                        # Parse Org
                        org = "Devnovate"
                        if 'Organized by' in text_list:
                            idx = text_list.index('Organized by')
                            if len(text_list) > idx + 1:
                                org = text_list[idx + 1]
                                
                        # Parse Prize
                        prize = 0
                        for t in text_list:
                            if any(x in t for x in ['₹', 'INR', 'Rs']):
                                try:
                                    num_str = ''.join(filter(str.isdigit, t))
                                    if num_str:
                                        val = int(num_str)
                                        if val > prize: prize = val
                                except: pass
                                
                        # Parse Date (e.g., '01-02-2026' or 'Starts 02-04-2026')
                        date_str = datetime.now().isoformat()
                        for t in text_list:
                            match = re.search(r'(\d{2}-\d{2}-\d{4})', t)
                            if match:
                                date_str = match.group(1)
                                break
                            
                        # Theme (first real tag usually)
                        theme = "Open Theme"
                        for t in text_list:
                            if t not in ['ONLINE', 'OFFLINE', 'HYBRID', 'OPEN', 'Organized by', org, 'Apply Now'] and 'registered' not in t and 'Starts' not in t and not 'Tags' in t and len(t) < 30:
                                theme = t
                                break
                                
                        apply_url = f'https://devnovate.co{href}' if href.startswith('/') else href
                        
                        # Duplicate check
                        if not any(h.get('applyUrl') == apply_url for h in hackathons):
                            hackathons.append({
                                "id": str(uuid.uuid4()),
                                "title": title,
                                "organization": org,
                                "type": h_type,
                                "theme": theme,
                                "prizePool": prize,
                                "startDate": date_str,
                                "endDate": date_str,
                                "applyUrl": apply_url,
                                "source": "Devnovate"
                            })
                            
        except Exception as e:
            print(f"Error scraping Devnovate: {e}")
        finally:
            await browser.close()
            
    return hackathons

async def scrape_devnovate_events():
    def _run_in_thread():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(_scrape_devnovate_async())
    
    return await asyncio.to_thread(_run_in_thread)

if __name__ == "__main__":
    res = asyncio.run(scrape_devnovate_events())
    print(json.dumps(res, indent=2))
