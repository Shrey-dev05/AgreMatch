import os
import io
import re
import json
from typing import Dict, Any, List

# Try importing PDF reader
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None

# Skill taxonomy for intelligent NLP extraction
SKILL_TAXONOMY = {
    # Languages
    "Python": ["python", "py", "python3"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "C++": ["c++", "cpp"],
    "C": [r"\bc\b", "c language"],
    "Java": ["java", "jvm"],
    "Go": ["golang", r"\bgo\b"],
    "Rust": ["rust", "cargo"],
    "SQL": ["sql", "postgresql", "postgres", "mysql", "sqlite", "nosql", "mongodb"],
    "HTML/CSS": ["html", "html5", "css", "css3", "sass", "scss"],
    "Solidity": ["solidity", "web3", "smart contracts", "ethereum", "evm"],
    
    # Frameworks & Libraries
    "React": ["react", "react.js", "reactjs"],
    "Next.js": ["next.js", "nextjs", "next 14", "next 15", "next 16"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Express.js": ["express", "express.js", "expressjs"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    
    # AI & ML
    "Machine Learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "Deep Learning": ["deep learning", "neural networks", "cnn", "rnn", "transformer"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "keras"],
    "LLMs & GenAI": ["llm", "llms", "large language models", "genai", "generative ai", "langchain", "gemini", "openai", "gpt", "rag"],
    "Computer Vision": ["computer vision", "opencv", "yolo", "image processing"],
    "NLP": ["nlp", "natural language processing", "bert", "spacy", "huggingface"],
    
    # Cloud & DevOps
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Google Cloud": ["gcp", "google cloud"],
    "Git & GitHub": ["git", "github", "version control"],
    "Linux": ["linux", "bash", "shell scripting", "ubuntu"],
    
    # Design & Product
    "UI/UX Design": ["ui/ux", "ui design", "ux design", "figma", "wireframing", "prototyping", "user research"],
}

# Theme to Skill affinity matrix for Hackathon matching
THEME_AFFINITIES = {
    "ai": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "LLMs & GenAI", "NLP", "FastAPI"],
    "machine learning": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "SQL"],
    "data": ["Python", "SQL", "Machine Learning", "PyTorch"],
    "web3": ["Solidity", "TypeScript", "JavaScript", "React", "Next.js"],
    "blockchain": ["Solidity", "Rust", "Go", "TypeScript", "Web3"],
    "full stack": ["React", "Next.js", "Node.js", "TypeScript", "Python", "FastAPI", "SQL", "Tailwind CSS"],
    "open innovation": ["Python", "React", "Next.js", "Node.js", "UI/UX Design", "Git & GitHub"],
    "smart cities": ["Python", "Machine Learning", "Docker", "React"],
    "healthtech": ["Python", "Machine Learning", "FastAPI", "UI/UX Design"],
    "fintech": ["Python", "SQL", "TypeScript", "FastAPI", "Docker", "React"],
    "clean tech": ["Python", "React", "UI/UX Design"],
    "ui/ux": ["UI/UX Design", "HTML/CSS", "React", "Tailwind CSS"],
    "coding": ["Python", "C++", "Java", "TypeScript"]
}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content from a PDF file safely, with robust fallbacks."""
    text = ""
    if PdfReader:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            if text.strip():
                return text.strip()
        except Exception as e:
            print(f"PdfReader warning: {e}")
            
    # Raw byte extraction fallback (handles test PDFs and raw text)
    try:
        raw = pdf_bytes.decode('utf-8', errors='ignore')
        clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', raw)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 10:
            return clean
    except:
        pass
        
    return text.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """Extracts known tech skills from raw text using regex patterns."""
    text_lower = " " + text.lower() + " "
    matched_skills = []
    
    for skill_name, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            if alias.startswith(r"\b"):
                pattern = alias
            else:
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                matched_skills.append(skill_name)
                break
                
    return matched_skills

def match_hackathons_to_resume(resume_text: str, hackathons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Intelligently analyzes candidate resume against a list of live hackathons.
    Returns:
    - Extracted skills
    - Suggested missing skills
    - Profile archetype / recommended role
    - Overall builder readiness score
    - Scored & ranked hackathons with matching reasons
    """
    extracted_skills = extract_skills_from_text(resume_text)
    
    # If very few skills found, provide sensible starter defaults
    if len(extracted_skills) < 2:
        extracted_skills = ["Python", "React", "Problem Solving", "Git & GitHub"]
        
    extracted_set = set(extracted_skills)
    
    # Determine candidate profile archetype
    has_ai = any(s in extracted_set for s in ["Machine Learning", "PyTorch", "TensorFlow", "LLMs & GenAI", "NLP"])
    has_web = any(s in extracted_set for s in ["React", "Next.js", "Node.js", "TypeScript", "FastAPI", "HTML/CSS"])
    has_web3 = "Solidity" in extracted_set
    has_design = "UI/UX Design" in extracted_set
    
    if has_ai and has_web:
        recommended_role = "Full-Stack AI Engineer"
    elif has_ai:
        recommended_role = "AI / ML Researcher & Builder"
    elif has_web3:
        recommended_role = "Web3 & Smart Contract Developer"
    elif has_design:
        recommended_role = "Product Designer & Frontend Hacker"
    elif has_web:
        recommended_role = "Full-Stack Web Developer"
    else:
        recommended_role = "Software Development Generalist"

    # Score each hackathon
    scored_hackathons = []
    
    for hack in hackathons:
        title = str(hack.get("title") or "").lower()
        raw_theme = hack.get("theme") or ""
        theme = (" ".join(str(t) for t in raw_theme) if isinstance(raw_theme, list) else str(raw_theme)).lower()
        desc = str(hack.get("description") or "").lower()
        combined_text = f"{title} {theme} {desc}"
        
        # Calculate affinity
        matching_skills = []
        target_skills = []
        
        for key, aff_skills in THEME_AFFINITIES.items():
            if key in combined_text:
                target_skills.extend(aff_skills)
                
        # If open innovation or unlisted, consider general web/software skills
        if not target_skills or "open" in theme or "innovation" in theme or "restrictions" in theme:
            target_skills = ["Python", "React", "TypeScript", "FastAPI", "UI/UX Design", "Docker"]
            
        target_set = set(target_skills)
        matching_skills = list(extracted_set.intersection(target_set))
        
        # Base score starts from match ratio
        if len(target_set) > 0:
            match_ratio = len(matching_skills) / min(len(target_set), 5)
            score = int(60 + (match_ratio * 38))
        else:
            score = 70
            
        # Give bonus if specific keywords match
        if any(s.lower() in combined_text for s in extracted_skills):
            score = min(99, score + 6)
            
        score = max(45, min(98, score))
        
        # Generate custom explanation
        if matching_skills:
            reason = f"High affinity! Your skills in {', '.join(matching_skills[:3])} directly match this event's focus."
        else:
            reason = f"Great challenge to apply your technical foundation in {', '.join(extracted_skills[:2])}."
            
        scored_h = dict(hack)
        scored_h["matchScore"] = score
        scored_h["matchReason"] = reason
        scored_h["matchingSkills"] = matching_skills
        scored_hackathons.append(scored_h)
        
    # Sort descending by match score
    scored_hackathons.sort(key=lambda x: x.get("matchScore", 0), reverse=True)
    
    # Compute overall profile readiness
    top_scores = [h.get("matchScore", 70) for h in scored_hackathons[:5]]
    overall_score = int(sum(top_scores) / len(top_scores)) if top_scores else 84
    
    # Suggest 3-4 complementary skills that would unlock even higher scores
    all_target_skills = set()
    for h in scored_hackathons[:10]:
        raw_th = h.get("theme") or ""
        th_str = (" ".join(str(t) for t in raw_th) if isinstance(raw_th, list) else str(raw_th)).lower()
        for key, aff in THEME_AFFINITIES.items():
            if key in th_str:
                all_target_skills.update(aff)
    suggested_skills = list(all_target_skills - extracted_set)[:4]
    if not suggested_skills:
        suggested_skills = ["Docker", "Vector DBs", "LangChain", "Tailwind CSS"]
        
    return {
        "success": True,
        "overallScore": overall_score,
        "profileSummary": f"Profile matches well with {len(scored_hackathons)} live competitions as a {recommended_role}.",
        "recommendedRole": recommended_role,
        "extractedSkills": extracted_skills,
        "suggestedSkills": suggested_skills,
        "matchedHackathons": scored_hackathons
    }
