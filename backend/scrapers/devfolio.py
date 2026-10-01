import httpx
from bs4 import BeautifulSoup
import uuid
import json
from datetime import datetime

async def scrape_devfolio_hackathons():
    """
    Scrapes live hackathons from https://devfolio.co/hackathons
    Devfolio SSR renders its query cache into __NEXT_DATA__.
    """
    url = "https://devfolio.co/hackathons"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    hackathons = []
    
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"[Devfolio] Error fetching page: status {resp.status_code}")
                return []
            
            soup = BeautifulSoup(resp.text, "html.parser")
            next_data_elem = soup.find("script", id="__NEXT_DATA__")
            
            if not next_data_elem or not next_data_elem.string:
                print("[Devfolio] __NEXT_DATA__ not found in page HTML")
                return []
            
            data = json.loads(next_data_elem.string)
            queries = data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
            
            items = []
            for q in queries:
                q_data = q.get("state", {}) .get("data", {})
                if isinstance(q_data, dict):
                    if "open_hackathons" in q_data and isinstance(q_data["open_hackathons"], list):
                        items.extend(q_data["open_hackathons"])
                    if "featured_hackathons" in q_data and isinstance(q_data["featured_hackathons"], list):
                        items.extend(q_data["featured_hackathons"])
                    if "upcoming_hackathons" in q_data and isinstance(q_data["upcoming_hackathons"], list):
                        items.extend(q_data["upcoming_hackathons"])
            
            seen_slugs = set()
            for item in items:
                slug = item.get("slug")
                if not slug or slug in seen_slugs:
                    continue
                seen_slugs.add(slug)
                
                title = item.get("name") or slug.replace("-", " ").title()
                is_online = item.get("is_online", True)
                h_type = "virtual" if is_online else "in-person"
                
                # Extract themes
                themes_list = item.get("themes") or []
                theme_names = []
                for t in themes_list:
                    if isinstance(t, dict):
                        t_obj = t.get("theme", {})
                        if isinstance(t_obj, dict) and "name" in t_obj:
                            theme_names.append(t_obj["name"])
                        elif "name" in t:
                            theme_names.append(t["name"])
                theme = ", ".join(theme_names) if theme_names else "Open Innovation"
                
                # Dates
                start_date = item.get("starts_at") or datetime.utcnow().isoformat()
                end_date = item.get("ends_at") or start_date
                
                # Apply URL
                settings = item.get("settings") or {}
                external_url = settings.get("external_apply_url") or settings.get("site")
                apply_url = external_url if (external_url and "http" in external_url) else f"https://{slug}.devfolio.co"
                
                # Organization
                org = "Devfolio Community"
                if settings.get("twitter"):
                    handle = settings["twitter"].rstrip("/").split("/")[-1]
                    if handle:
                        org = handle.replace("_", " ").title()
                
                hackathons.append({
                    "id": f"devfolio-{item.get('uuid') or slug}",
                    "title": title,
                    "organization": org,
                    "type": h_type,
                    "theme": theme,
                    "prizePool": 0, # Devfolio displays specific sponsor bounties on event pages
                    "startDate": start_date,
                    "endDate": end_date,
                    "applyUrl": apply_url,
                    "source": "Devfolio",
                    "location": "Online" if is_online else "On Campus / In-Person",
                    "participants": item.get("participants_count", 0)
                })
                
    except Exception as e:
        print(f"[Devfolio] Scraping error: {e}")
        
    return hackathons

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(scrape_devfolio_hackathons())
    print(f"Scraped {len(results)} Devfolio hackathons:")
    for h in results[:3]:
        print(json.dumps(h, indent=2))
