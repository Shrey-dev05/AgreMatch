import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import uuid
import json
import sys
from datetime import datetime

async def _scrape_unstop_async():
    url_target = "https://unstop.com/hackathons?oppstatus=open"
    hackathons = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"Navigating to {url_target}...")
            await page.goto(url_target, timeout=60000)
            await page.wait_for_timeout(5000)
            
            # Scroll to load a few more
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            seen = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/hackathons/' in href.lower() or '/competitions/' in href.lower():
                    apply_url = f'https://unstop.com{href}' if href.startswith('/') else href
                    if apply_url in seen: continue
                    seen.add(apply_url)
                    
                    container = a.find_parent('div', class_=lambda c: c and ('listing' in c or 'card' in c or 'box' in c)) or a
                    title_elem = container.find(['h2', 'h3'])
                    title = title_elem.text.strip() if title_elem else 'Unknown Hackathon'
                    
                    if title == 'Unknown Hackathon': continue
                    
                    texts = [t.strip() for t in container.find_all(string=True) if t.strip()]
                    
                    # Try to extract the Org
                    org = texts[1] if len(texts) > 1 else 'Unstop'
                    if 'KLE' in org or 'College' in org or 'Institute' in org or 'University' in org:
                        pass # keep it
                    else:
                        for t in texts[1:]:
                            if 'College' in t or 'Institute' in t or 'University' in t or 'Academy' in t:
                                org = t
                                break
                    
                    # Parse type (Unstop defaults to online unless specified in tags)
                    h_type = 'virtual'
                    for t in texts:
                        t_lower = t.lower()
                        if 'offline' in t_lower or 'in-person' in t_lower or 'campus' in t_lower:
                            h_type = 'in-person'
                            break
                        elif 'hybrid' in t_lower:
                            h_type = 'hybrid'
                            break
                            
                    # Find theme
                    theme = 'Open Innovation'
                    for t in texts:
                        if t not in [title, org, 'offline', 'online', 'hybrid'] and len(t) < 30 and 'days' not in t.lower() and 'left' not in t.lower() and 'team' not in t.lower():
                            if not any(x in t for x in ['₹', 'INR', 'Rs']) and not t.replace(',', '').isdigit():
                                theme = t
                                break
                    
                    prize = 0
                    date_str = datetime.now().isoformat()
                    
                    for t in texts:
                        if 'days left' in t.lower() or 'registered' in t.lower() or 'team' in t.lower(): continue
                        
                        # Find Unstop prizes like '1,00,000' or '₹ 50,000'
                        if any(x in t for x in ['₹', 'INR', 'Rs']) or (t.replace(',', '').isdigit() and len(t) > 3):
                            try:
                                num_str = ''.join(filter(str.isdigit, t))
                                if num_str:
                                    val = int(num_str)
                                    if val > prize and val < 10000000: prize = val
                            except: pass
                            
                        match = re.search(r'(\d{2} \w{3} \d{2})|(\d{1,2}/\d{1,2}/\d{2,4})', t)
                        if match:
                            date_str = match.group(0)
                    
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
                        "source": "Unstop"
                    })
                            
        except Exception as e:
            print(f"Error scraping Unstop: {e}")
        finally:
            await browser.close()
            
    return hackathons

async def scrape_unstop_hackathons():
    def _run_in_thread():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(_scrape_unstop_async())
    
    return await asyncio.to_thread(_run_in_thread)

if __name__ == "__main__":
    res = asyncio.run(scrape_unstop_hackathons())
    print(json.dumps(res, indent=2))
