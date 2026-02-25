import sys
import asyncio
import time

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import traceback
from ai_parser import extract_text_from_pdf, generate_compatibility_score

app = FastAPI(title="Agreggator AI Backend")

# Allowing CORS for local Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache to prevent slow repeated scraping
CACHE = {}
CACHE_TTL = 3600 # 1 hour in seconds

async def get_cached_or_scrape(key: str, scrape_func, timeout=30.0):
    now = time.time()
    if key in CACHE:
        data, timestamp = CACHE[key]
        if now - timestamp < CACHE_TTL:
            return data
            
    try:
        # Wrap the scraper with a timeout so it doesn't hang the API indefinitely
        data = await asyncio.wait_for(scrape_func(), timeout=timeout)
        CACHE[key] = (data, now)
        return data
    except asyncio.TimeoutError:
        print(f"Timeout while scraping {key}")
        # Return empty or old data if it timed out to prevent complete failure
        if key in CACHE:
            return CACHE[key][0]
        return []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agreggator AI Parser API"}

@app.post("/api/parse-resume")
async def parse_resume(
    resume: UploadFile = File(...),
    description: str = Form(None),
    is_hackathon: bool = Form(False)
):
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
    items: str = Form(...)  # Expected to be a JSON string of item dicts
):
    if not resume.filename.endswith('.pdf') and not resume.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported")
        
    try:
        import json
        items_list = json.loads(items)
        
        pdf_bytes = await resume.read()
        
        # Determine extraction strategy based on filetype
        if resume.filename.endswith('.pdf'):
            text = extract_text_from_pdf(pdf_bytes)
        else:
            text = "DOCX extraction not natively supported yet, defaulting to empty text."
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from the document")
            
        from ai_parser import generate_batch_compatibility_scores
        
        results = generate_batch_compatibility_scores(text, items_list, is_hackathon=False)
        return {"success": True, "data": results}
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/devpost")
async def get_devpost_hackathons():
    from scrapers.devpost import scrape_devpost_hackathons
    try:
        data = await get_cached_or_scrape("devpost_hackathons", scrape_devpost_hackathons)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/devnovate")
async def get_devnovate_hackathons():
    from scrapers.devnovate import scrape_devnovate_events
    try:
        data = await get_cached_or_scrape("devnovate_hackathons", scrape_devnovate_events)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hackathons/scrape/unstop")
async def get_unstop_hackathons():
    from scrapers.unstop import scrape_unstop_hackathons
    try:
        data = await get_cached_or_scrape("unstop_hackathons", scrape_unstop_hackathons)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/internships/scrape/aicte")
async def get_aicte_internships():
    from scrapers.aicte import scrape_aicte_internships
    try:
        data = await get_cached_or_scrape("aicte_internships", scrape_aicte_internships)
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
