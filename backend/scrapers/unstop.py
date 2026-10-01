import httpx
import re
import json
from datetime import datetime

async def scrape_unstop_hackathons():
    """
    Scrapes live hackathons from Unstop using their public API endpoint matching:
    https://unstop.com/hackathons?oppstatus=open&usertype=students&domain=2&course=6&passingOutYear=2028
    Plus general open hackathons for students to guarantee comprehensive results.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://unstop.com/hackathons?oppstatus=open&usertype=students&domain=2&course=6&passingOutYear=2028",
    }
    
    # We query the user-specified student filter first, then general open hackathons to gather rich listings
    urls = [
        "https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=open&usertype=students&domain=2&course=6&passingOutYear=2028&per_page=15",
        "https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=open&per_page=20"
    ]
    
    hackathons = []
    seen_ids = set()
    
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
            for url in urls:
                try:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    
                    data = resp.json()
                    items = data.get("data", {}).get("data", [])
                    
                    for item in items:
                        item_id = str(item.get("id"))
                        if not item_id or item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)
                        
                        title = item.get("title") or "Unstop Hackathon"
                        
                        # Organization
                        org_info = item.get("organisation") or {}
                        if isinstance(org_info, dict):
                            org = org_info.get("name") or "Unstop Partner"
                        else:
                            org = str(org_info)
                            
                        # Apply URL
                        seo_url = item.get("seo_url")
                        public_url = item.get("public_url")
                        if seo_url and seo_url.startswith("http"):
                            apply_url = seo_url
                        elif public_url:
                            apply_url = f"https://unstop.com/{public_url}" if not public_url.startswith("http") else public_url
                        else:
                            apply_url = f"https://unstop.com/hackathons/{item_id}"
                            
                        # Type
                        h_type = "virtual"
                        locations = item.get("locations") or []
                        region = (item.get("region") or "").lower()
                        if locations or "offline" in region or "campus" in region:
                            h_type = "in-person"
                        elif "hybrid" in region:
                            h_type = "hybrid"
                            
                        # Theme
                        filters = item.get("filters") or []
                        themes = [f.get("name") for f in filters if isinstance(f, dict) and f.get("name") and f.get("name") != "All"]
                        theme = ", ".join(themes[:2]) if themes else "Engineering & Coding"
                        
                        # Prize
                        prizes = item.get("prizes") or item.get("prize") or 0
                        prize_val = 0
                        if isinstance(prizes, (int, float)):
                            prize_val = int(prizes)
                        elif isinstance(prizes, str):
                            digits = re.sub(r"[^\d]", "", prizes)
                            if digits:
                                try:
                                    prize_val = int(digits)
                                except ValueError:
                                    prize_val = 0
                        elif isinstance(prizes, list) and prizes:
                            first_p = prizes[0]
                            if isinstance(first_p, dict):
                                cash = first_p.get("cash") or first_p.get("amount") or 0
                                digits = re.sub(r"[^\d]", "", str(cash))
                                if digits:
                                    prize_val = int(digits)
                        
                        # Dates
                        start_date = item.get("start_date") or item.get("approved_date") or datetime.utcnow().isoformat()
                        end_date = item.get("end_date") or start_date
                        
                        loc_name = "Online"
                        if locations and isinstance(locations, list):
                            first_loc = locations[0]
                            if isinstance(first_loc, dict):
                                loc_name = first_loc.get("city") or first_loc.get("state") or "In-Person"
                            elif isinstance(first_loc, str):
                                loc_name = first_loc
                        elif h_type == "in-person":
                            loc_name = "College / Campus"
                        
                        hackathons.append({
                            "id": f"unstop-{item_id}",
                            "title": title,
                            "organization": org,
                            "type": h_type,
                            "theme": theme,
                            "prizePool": prize_val,
                            "startDate": str(start_date),
                            "endDate": str(end_date),
                            "applyUrl": apply_url,
                            "source": "Unstop",
                            "location": loc_name,
                            "participants": item.get("registerCount", 0)
                        })
                except Exception as sub_e:
                    print(f"[Unstop] Error querying endpoint {url}: {sub_e}")
                    
    except Exception as e:
        print(f"[Unstop] Scraping error: {e}")
        
    return hackathons

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(scrape_unstop_hackathons())
    print(f"Scraped {len(results)} Unstop hackathons:")
    for h in results[:3]:
        print(f"- {h['title']} by {h['organization']} ({h['type']})")
