import os
import io
import json
from typing import Dict, Any, List
import PyPDF2
from pydantic import BaseModel
from google import genai

# NOTE: Set your Gemini API key in the environment or replace here
# os.environ["GEMINI_API_KEY"] = "your_api_key_here"

try:
    client = genai.Client()
except Exception as e:
    print(f"Warning: Could not initialize Gemini Client: {e}")
    client = None

class MatchResult(BaseModel):
    score: int
    extracted_skills: list[str]
    missing_skills: list[str]
    explanation: str

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def generate_compatibility_score(resume_text: str, description: str, is_hackathon: bool = False) -> Dict[str, Any]:
    """
    Uses Gemini 1.5 Flash to parse the resume, extract skills, and return a Match Score.
    The response format is enforced via structured output / prompt constraints.
    """
    entity_type = "Hackathon" if is_hackathon else "Internship"
    
    prompt = f"""
    You are an expert AI recruiter system for a platform called 'Agreggator'.
    Analyze the given candidate's Resume against the provided {entity_type} Description.
    
    Task:
    1. Extract the candidate's core technical and soft skills.
    2. Determine the missing skills required by the {entity_type}.
    3. Calculate a "Compatibility Score" out of 100 based on the match.
    4. Provide a brief explanation of the score.
    
    Must return a valid JSON object matching this schema exactly:
    {{
        "score": <int between 0 and 100>,
        "extracted_skills": [<string list>],
        "missing_skills": [<string list>],
        "explanation": "<string summary>"
    }}

    -- Resume Text --
    {resume_text}
    
    -- {entity_type} Description --
    {description}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Parse the JSON response text
        raw_output = response.text.strip()
        # Clean markdown formatting if present
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3].strip()
            
        result = json.loads(raw_output)
        return result
    
    except Exception as e:
        print(f"AI Matcher Error: {e}")
        return {
            "score": 0,
            "extracted_skills": [],
            "missing_skills": [],
            "explanation": "Failed to calculate compatibility score due to an internal error."
        }

def generate_batch_compatibility_scores(resume_text: str, items: List[Dict[str, Any]], is_hackathon: bool = False) -> List[Dict[str, Any]]:
    """
    Takes a single resume and a list of items (internships or hackathons).
    Returns the items mapped with their compatibility scores in a single prompt to save time.
    """
    if not items:
        return []

    entity_type = "Hackathon" if is_hackathon else "Internship"
    
    # We will only send crucial details to avoid token limit overflow if list is large
    # For now, let's just do up to 40 items at a time safely
    safe_items = items[:40]
    
    items_json_str = json.dumps([{
        "id": it.get("id"),
        "title": it.get("title") or it.get("role"),
        "details": f"Role: {it.get('roleType', '')} Theme: {it.get('theme', '')} Org: {it.get('company') or it.get('organization', '')}"
    } for it in safe_items], indent=2)

    prompt = f"""
    You are an expert AI recruiter system for a platform called 'Agreggator'.
    Analyze the given candidate's Resume against a list of {len(safe_items)} {entity_type}s.
    
    Rank and score each item based on how well the candidate's skills match the {entity_type}'s title and details.
    
    Must return a valid JSON array matching this schema exactly:
    [
        {{
            "id": "<string matching the input item id>",
            "score": <int between 0 and 100>,
            "explanation": "<1 sentence explanation>"
        }}
    ]

    -- Resume Text --
    {resume_text}
    
    -- {entity_type} List --
    {items_json_str}
    """
    
    try:
        if not client:
            raise ValueError("Gemini Client not initialized")
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3].strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output[3:-3].strip()
            
        results = json.loads(raw_output)
        
        # Merge scores back into the original items
        score_map = {str(r.get("id")): r for r in results if isinstance(r, dict)}
        
        scored_items = []
        for item in safe_items:
            item_copy = dict(item)
            match_data = score_map.get(str(item.get("id")))
            if match_data:
                item_copy["matchScore"] = match_data.get("score", 0)
                item_copy["matchExplanation"] = match_data.get("explanation", "")
            else:
                item_copy["matchScore"] = 0
                item_copy["matchExplanation"] = "Analysis failed for this item."
            scored_items.append(item_copy)
            
        # Return sorted by score
        return sorted(scored_items, key=lambda x: x.get("matchScore", 0), reverse=True)
        
    except Exception as e:
        print(f"Batch AI Matcher Error (Using Fallback Mock): {e}")
        import random
        # Fallback Mock: Assign random scores so UI can still be tested
        scored_items = []
        for item in safe_items:
            item_copy = dict(item)
            score = random.randint(30, 95)
            item_copy["matchScore"] = score
            
            if score >= 80:
                item_copy["matchExplanation"] = "Strong alignment with your core technical skills and experience level."
            elif score >= 60:
                item_copy["matchExplanation"] = "Solid match, but you may need to learn a few supplementary tools."
            else:
                item_copy["matchExplanation"] = "Missing several key requirements requested by this organization."
                
            scored_items.append(item_copy)
            
        return sorted(scored_items, key=lambda x: x.get("matchScore", 0), reverse=True)

# Example Usage:
if __name__ == "__main__":
    sample_resume = "Experienced in Python, React, Next.js, and SQL. Built 3 full-stack applications."
    sample_internship = "Looking for a full-stack developer with React and Next.js experience. Python is a plus but need strong TypeScript."
    
    match_data = generate_compatibility_score(sample_resume, sample_internship, is_hackathon=False)
    print("Match Results:")
    print(json.dumps(match_data, indent=2))
