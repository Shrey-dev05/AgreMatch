import httpx
import re
import json
from datetime import datetime

async def scrape_devnovate_events():
    """
    Scrapes live hackathons/events from https://devnovate.co/events
    via Devnovate's public event search API.
    """
    url = "https://devnovate.co/api/v1/events/search?page=1&limit=20&search=&filter=all"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://devnovate.co",
        "Referer": "https://devnovate.co/events",
    }
    
    hackathons = []
    
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"[Devnovate] Error fetching events: status {resp.status_code}")
                return []
            
            data = resp.json()
            events = data.get("events") or data.get("data") or []
            
            for item in events:
                event_id = item.get("_id") or str(item.get("id", ""))
                title = item.get("eventName") or item.get("name") or "Devnovate Hackathon"
                org = item.get("organizationName") or item.get("organizer") or "Devnovate"
                
                # Location and type
                loc = (item.get("location") or "").strip()
                loc_lower = loc.lower()
                if "offline" in loc_lower or "in-person" in loc_lower or "campus" in loc_lower or "hall" in loc_lower:
                    h_type = "in-person"
                elif "hybrid" in loc_lower:
                    h_type = "hybrid"
                else:
                    h_type = "virtual"
                
                theme = item.get("theme") or "Tech & Innovation"
                
                # Prize pool extraction
                prize_raw = item.get("prizePool") or item.get("prizes") or 0
                prize_val = 0
                if isinstance(prize_raw, (int, float)):
                    prize_val = int(prize_raw)
                elif isinstance(prize_raw, str):
                    digits = re.sub(r"[^\d]", "", prize_raw)
                    if digits:
                        try:
                            prize_val = int(digits)
                        except ValueError:
                            prize_val = 0
                
                # Dates
                start_date = item.get("startDate") or item.get("registrationDeadline") or datetime.utcnow().isoformat()
                end_date = item.get("endDate") or start_date
                
                apply_url = f"https://devnovate.co/events/{event_id}" if event_id else "https://devnovate.co/events"
                
                hackathons.append({
                    "id": f"devnovate-{event_id}",
                    "title": title,
                    "organization": org,
                    "type": h_type,
                    "theme": theme,
                    "prizePool": prize_val,
                    "startDate": str(start_date),
                    "endDate": str(end_date),
                    "applyUrl": apply_url,
                    "source": "Devnovate",
                    "location": loc if loc else ("Online" if h_type == "virtual" else "In-Person"),
                    "participants": item.get("numberOfRegistrations", 0)
                })
                
    except Exception as e:
        print(f"[Devnovate] Scraping error: {e}")
        
    return hackathons

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(scrape_devnovate_events())
    print(f"Scraped {len(results)} Devnovate hackathons:")
    for h in results[:3]:
        print(f"- {h['title']} by {h['organization']} ({h['type']}) Prize: {h['prizePool']}")
