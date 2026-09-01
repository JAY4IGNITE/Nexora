import os
import json
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.core.supabase import get_supabase_client

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))

# Setup Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")
client = genai.Client(api_key=api_key)

class CourseModule(BaseModel):
    name: str
    description: Optional[str] = None
    topics: List[str]

class ExtractedCourse(BaseModel):
    course_code: str
    course_title: str
    semester: str
    credits: int
    course_objectives: Optional[str] = None
    learning_outcomes: List[str]
    candidate_skills: List[str]
    modules: List[CourseModule]

class ExtractionResult(BaseModel):
    courses: List[ExtractedCourse]

def extract_pdf_text_from_transcript(transcript_path: str) -> str:
    """Extracts the embedded OCR text from the agent transcript."""
    text_content = ""
    found_start = False
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        # Search backwards or just read all and find the block
        lines = f.readlines()
        for line in lines:
            try:
                data = json.loads(line)
                if data.get('type') == 'USER_INPUT':
                    content = data.get('content', '')
                    if '==Start of PDF==' in content:
                        start_idx = content.find('==Start of PDF==')
                        end_idx = content.find('==End of PDF==')
                        if end_idx != -1:
                            return content[start_idx:end_idx]
            except:
                pass
    return ""

async def extract_courses_from_text(chunk: str, page_num: int) -> dict:
    """Uses Gemini to extract structured JSON from a text chunk."""
    prompt = f"""
    You are an expert curriculum data extractor. 
    Extract the courses defined in this text from the AICTE Model Curriculum.
    
    TEXT CHUNK:
    {chunk}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult
            )
        )
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        print(f"Error extracting from chunk (Page {page_num}): {e}")
        
    return {"courses": []}

async def run_pipeline():
    print("--- STARTING AICTE EXTRACTION PIPELINE ---")
    
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'curriculum', 'aicte', 'aicte_subset.txt')
    print("1. Extracting text from local file...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        pdf_text = f.read()
    
    if not pdf_text:
        print("FAIL: Could not read text file.")
        return
        
    print(f"Found text: {len(pdf_text)} characters.")
    
    # Split text into chunks 
    pages = [pdf_text] # Since it's a small subset, treat it as one page
    
    db = get_supabase_client()
    total_courses_extracted = 0
    total_topics = 0
    total_outcomes = 0
    total_skills = 0
    semesters = set()
    errors = 0
    
    print(f"2. Processing text via Gemini...")
    
    for i, page_content in enumerate(pages):
        page_num = 1
        try:
            result = await extract_courses_from_text(page_content, page_num)
            courses = result.get('courses', [])
            
            if not courses:
                print("No courses found in response.")
                continue
                
            # Store in raw_curriculum_extractions
            raw_record = {
                "source": "AICTE",
                "source_document": "AICTE UG CSE Model Curriculum",
                "extracted_page": page_num,
                "raw_json": result,
                "status": "EXTRACTED"
            }
            db.table('raw_curriculum_extractions').insert(raw_record).execute()
            
            for c in courses:
                total_courses_extracted += 1
                semesters.add(c.get('semester'))
                total_outcomes += len(c.get('learning_outcomes', []))
                total_skills += len(c.get('candidate_skills', []))
                
                for m in c.get('modules', []):
                    total_topics += len(m.get('topics', []))
            
        except Exception as e:
            errors += 1
            print(f"Error on page {page_num}: {e}")
            
    print("\n--- EXTRACTION COMPLETE ---")
    print(f"1. Number of courses extracted: {total_courses_extracted}")
    print(f"2. Number of semesters: {len(semesters)}")
    print(f"3. Number of topics: {total_topics}")
    print(f"4. Number of learning outcomes: {total_outcomes}")
    print(f"5. Number of candidate skills: {total_skills}")
    print(f"6. Extraction errors: {errors}")
    print(f"7. Ambiguous mappings: Pending Normalization Phase")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
