import asyncio
from playwright.async_api import async_playwright
import sys
from bs4 import BeautifulSoup

async def debug_click():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('https://internship.aicte-india.org/recentlyposted.php', timeout=60000)
        await page.wait_for_timeout(3000)
        
        for i in range(4):
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.find_all('div', class_=lambda c: c and 'card' in c)
            if cards:
                t = [t.strip() for t in cards[0].find_all(string=True) if t.strip()]
                print(f'Page {i+1} first title: {t[0] if t else "Unknown"}')
                
            if i < 3:
                btn = await page.query_selector("a.page-link:has-text('Next')")
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(4000)
                else: break
        await b.close()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
asyncio.run(debug_click())

