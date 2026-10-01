import sys
import asyncio
import time
import os
import json
import uuid
import traceback
import re
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from scrapers.devfolio import scrape_devfolio_hackathons
from scrapers.devnovate import scrape_devnovate_events
from scrapers.unstop import scrape_unstop_hackathons

app = FastAPI(
    title="Hackathon & Opportunity Aggregator API",
    description="Aggregates live hackathons from Devfolio, Devnovate, Unstop, and supports local campus hackathons.",
    version="2.0.0"
)

# Allowing CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_HACKATHONS_FILE = DATA_DIR / "local_hackathons.json"

# In-memory cache
CACHE = {}
CACHE_TTL = 1800 # 30 minutes in seconds

def load_local_hackathons() -> list:
    if not LOCAL_HACKATHONS_FILE.exists():
        return []
    try:
        with open(LOCAL_HACKATHONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading local hackathons: {e}")
        return []

def save_local_hackathons(hackathons: list):
    try:
        with open(LOCAL_HACKATHONS_FILE, "w", encoding="utf-8") as f:
            json.dump(hackathons, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving local hackathons: {e}")

class LocalHackathonCreate(BaseModel):
    title: str = Field(..., min_length=3)
    organization: str = Field(..., min_length=2)
    type: str = Field(default="in-person") # 'virtual' | 'in-person' | 'hybrid'
    theme: str = Field(default="Open Innovation")
    prizePool: Optional[int] = 0
    startDate: str
    endDate: str
    applyUrl: str
    location: Optional[str] = "Campus / Local Venue"
    contactEmail: Optional[str] = ""
    description: Optional[str] = ""

async def get_cached_or_scrape(key: str, scrape_func, force_refresh: bool = False, timeout=25.0):
    now = time.time()
    if not force_refresh and key in CACHE:
        data, timestamp = CACHE[key]
        if now - timestamp < CACHE_TTL:
            return data
            
    try:
        data = await asyncio.wait_for(scrape_func(), timeout=timeout)
        CACHE[key] = (data, now)
        return data
    except asyncio.TimeoutError:
        print(f"Timeout while scraping {key}")
        if key in CACHE:
            return CACHE[key][0]
        return []
    except Exception as e:
        print(f"Scraper error for {key}: {e}")
        traceback.print_exc()
        if key in CACHE:
            return CACHE[key][0]
        return []

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Hackathon Aggregator API",
        "version": "2.0.0",
        "endpoints": [
            "/api/hackathons/scrape/all",
            "/api/hackathons/scrape/devfolio",
            "/api/hackathons/scrape/devnovate",
            "/api/hackathons/scrape/unstop",
            "/api/hackathons/local",
            "/api/stats"
        ]
    }

@app.get("/api/hackathons/scrape/devfolio")
async def get_devfolio_hackathons(refresh: bool = Query(False)):
    try:
        data = await get_cached_or_scrape("devfolio", scrape_devfolio_hackathons, force_refresh=refresh)
        return {"success": True, "count": len(data), "source": "Devfolio", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/devnovate")
async def get_devnovate_hackathons(refresh: bool = Query(False)):
    try:
        data = await get_cached_or_scrape("devnovate", scrape_devnovate_events, force_refresh=refresh)
        return {"success": True, "count": len(data), "source": "Devnovate", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/unstop")
async def get_unstop_hackathons(refresh: bool = Query(False)):
    try:
        data = await get_cached_or_scrape("unstop", scrape_unstop_hackathons, force_refresh=refresh)
        return {"success": True, "count": len(data), "source": "Unstop", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/all")
async def get_all_hackathons(refresh: bool = Query(False)):
    """
    Aggregates hackathons concurrently from Devfolio, Devnovate, Unstop,
    and includes locally listed hackathons.
    """
    try:
        # Run all three scrapers concurrently
        devf_task = get_cached_or_scrape("devfolio", scrape_devfolio_hackathons, force_refresh=refresh)
        devn_task = get_cached_or_scrape("devnovate", scrape_devnovate_events, force_refresh=refresh)
        unst_task = get_cached_or_scrape("unstop", scrape_unstop_hackathons, force_refresh=refresh)
        
        devf_res, devn_res, unst_res = await asyncio.gather(
            devf_task, devn_task, unst_task, return_exceptions=True
        )
        
        devfolio_items = devf_res if isinstance(devf_res, list) else []
        devnovate_items = devn_res if isinstance(devn_res, list) else []
        unstop_items = unst_res if isinstance(unst_res, list) else []
        local_items = load_local_hackathons()
        
        combined = []
        combined.extend(local_items) # Local campus hackathons prioritized
        combined.extend(devfolio_items)
        combined.extend(devnovate_items)
        combined.extend(unstop_items)
        
        # Deduplicate by applyUrl or title
        seen = set()
        deduped = []
        for h in combined:
            key = (h.get("title", "").strip().lower(), h.get("source", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(h)
                
        return {
            "success": True,
            "totalCount": len(deduped),
            "sources": {
                "devfolio": len(devfolio_items),
                "devnovate": len(devnovate_items),
                "unstop": len(unstop_items),
                "local": len(local_items),
            },
            "data": deduped
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Local Hackathon Management
@app.get("/api/hackathons/local")
def list_local_hackathons():
    items = load_local_hackathons()
    return {"success": True, "count": len(items), "data": items}

@app.post("/api/hackathons/local")
def create_local_hackathon(hack: LocalHackathonCreate):
    items = load_local_hackathons()
    new_item = {
        "id": f"local-{uuid.uuid4().hex[:8]}",
        "title": hack.title,
        "organization": hack.organization,
        "type": hack.type,
        "theme": hack.theme,
        "prizePool": hack.prizePool or 0,
        "startDate": hack.startDate,
        "endDate": hack.endDate,
        "applyUrl": hack.applyUrl,
        "source": "Local Campus",
        "location": hack.location or "College / Local Campus",
        "contactEmail": hack.contactEmail,
        "description": hack.description,
        "participants": 0,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    items.insert(0, new_item)
    save_local_hackathons(items)
    return {"success": True, "message": "Local hackathon listed successfully!", "data": new_item}

@app.delete("/api/hackathons/local/{hackathon_id}")
def delete_local_hackathon(hackathon_id: str):
    items = load_local_hackathons()
    initial_len = len(items)
    items = [h for h in items if h.get("id") != hackathon_id]
    if len(items) == initial_len:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    save_local_hackathons(items)
    return {"success": True, "message": f"Deleted local hackathon {hackathon_id}"}

# Portal Stats
@app.get("/api/stats")
async def get_portal_stats():
    all_data = await get_all_hackathons()
    data = all_data.get("data", [])
    total_prize = sum(
        h.get("prizePool", 0) for h in data if isinstance(h.get("prizePool"), (int, float))
    )
    return {
        "success": True,
        "totalHackathons": len(data),
        "totalPrizePool": total_prize,
        "sourcesCount": all_data.get("sources", {}),
        "virtualCount": sum(1 for h in data if h.get("type") == "virtual"),
        "inPersonCount": sum(1 for h in data if h.get("type") == "in-person"),
        "hybridCount": sum(1 for h in data if h.get("type") == "hybrid"),
    }

@app.post("/api/hackathons/match-resume")
async def match_resume_with_hackathons(
    resume: UploadFile = File(...)
):
    """
    Parses candidate resume and computes personalized compatibility
    scores against all live hackathons currently aggregated on the portal.
    """
    from ai_parser import extract_text_from_pdf, match_hackathons_to_resume
    
    filename = (resume.filename or "").lower()
    if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Supported formats: PDF, DOCX, TXT")
        
    try:
        content_bytes = await resume.read()
        
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(content_bytes)
        elif filename.endswith('.txt'):
            text = content_bytes.decode('utf-8', errors='ignore')
        else: # docx
            # simple text extraction from docx byte stream
            try:
                raw_str = content_bytes.decode('utf-8', errors='ignore')
                text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', raw_str)
            except:
                text = ""
                
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract readable text from document. Please ensure file contains selectable text.")
            
        # Get all live hackathons
        all_res = await get_all_hackathons()
        hackathons_list = all_res.get("data", [])
        
        # Run matching engine
        match_result = match_hackathons_to_resume(text, hackathons_list)
        return match_result
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Resume matching failed: {str(e)}")

# Resume Parsing Endpoints (kept for compatibility)
@app.post("/api/parse-resume")
async def parse_resume(
    resume: UploadFile = File(...),
    description: str = Form(None),
    is_hackathon: bool = Form(False)
):
    from ai_parser import extract_text_from_pdf, generate_compatibility_score
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently")
        
    try:
        pdf_bytes = await resume.read()
        text = extract_text_from_pdf(pdf_bytes)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF")
            
        desc = description if description else "Looking for a software engineering candidate."
        result = generate_compatibility_score(text, desc, is_hackathon=is_hackathon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-resume-batch")
async def parse_resume_batch(
    resume: UploadFile = File(...),
    items: str = Form(...)
):
    from ai_parser import extract_text_from_pdf, generate_batch_compatibility_scores
    if not resume.filename.endswith('.pdf') and not resume.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported")
        
    try:
        items_list = json.loads(items)
        pdf_bytes = await resume.read()
        text = extract_text_from_pdf(pdf_bytes) if resume.filename.endswith('.pdf') else ""
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from document")
            
        results = generate_batch_compatibility_scores(text, items_list, is_hackathon=True)
        return {"success": True, "data": results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
