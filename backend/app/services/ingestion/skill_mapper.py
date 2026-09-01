import os
import json
import asyncio
from typing import List, Optional, Dict
from pydantic import BaseModel
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

class SkillMappingResult(BaseModel):
    mapped_skill: Optional[str]
    confidence: float

async def map_topic_to_skill_llm(topic: str, canonical_skills: List[str]) -> SkillMappingResult:
    """Uses Gemini to propose a canonical skill mapping for a given topic."""
    prompt = f"""
    You are an expert curriculum skill mapper.
    Map the raw curriculum topic: "{topic}" to the single closest canonical skill from this list.
    If none of the skills are a highly confident match, return null for mapped_skill.
    
    Canonical Skills List:
    {json.dumps(canonical_skills)}
    
    Return a JSON object matching the schema.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillMappingResult,
                temperature=0.0
            )
        )
        if response.text:
            data = json.loads(response.text)
            return SkillMappingResult(**data)
    except Exception as e:
        print(f"Error mapping topic via LLM: {e}")
        
    return SkillMappingResult(mapped_skill=None, confidence=0.0)

async def run_skill_mapping():
    print("--- STARTING SKILL MAPPING PIPELINE ---")
    db = get_supabase_client()
    
    # 1. Fetch canonical skills
    skills_response = db.table('skills').select('id, name, normalized_name').execute()
    canonical_skills_map = {s['normalized_name']: s for s in skills_response.data}
    canonical_skills_names = [s['name'] for s in skills_response.data]
    name_to_id_map = {s['name']: s['id'] for s in skills_response.data}
    
    # 2. Fetch raw extractions
    raw_extractions = db.table('raw_curriculum_extractions').select('*').eq('status', 'EXTRACTED').execute()
    
    if not raw_extractions.data:
        print("No raw extractions found with status 'EXTRACTED'.")
        return
        
    # Stats
    topics_processed = 0
    skills_mapped = 0
    confirmed = 0
    proposed = 0
    ambiguous = 0
    unmapped = 0
    
    # We need a dummy institution for the courses
    institution_res = db.table('users').select('id').eq('role', 'INSTITUTION').limit(1).execute()
    institution_id = institution_res.data[0]['id'] if institution_res.data else None
    
    for raw in raw_extractions.data:
        raw_json = raw['raw_json']
        source_page = raw['extracted_page']
        source_doc = raw['source_document']
        source = raw['source']
        
        courses = raw_json.get('courses', [])
        for c in courses:
            # Upsert Course
            course_res = db.table('courses').insert({
                'name': f"{c.get('course_code', '')} - {c.get('course_title', '')}".strip(" -"),
                'description': f"Credits: {c.get('credits', '')}",
                'provider_id': institution_id,
                'source': source,
                'source_document': source_doc,
                'source_page': source_page
            }).execute()
            
            if not course_res.data:
                continue
            course_id = course_res.data[0]['id']
            
            for idx, m in enumerate(c.get('modules', [])):
                # Upsert Module
                module_res = db.table('course_modules').insert({
                    'course_id': course_id,
                    'name': m['name'],
                    'description': m.get('description'),
                    'sequence': idx + 1,
                    'source': source,
                    'source_document': source_doc,
                    'source_page': source_page
                }).execute()
                
                if not module_res.data:
                    continue
                module_id = module_res.data[0]['id']
                
                # Process Topics
                for t in m.get('topics', []):
                    topics_processed += 1
                    
                    # Insert Topic
                    topic_res = db.table('course_topics').insert({
                        'course_module_id': module_id,
                        'name': t,
                        'source': source,
                        'source_document': source_doc,
                        'source_page': source_page
                    }).execute()
                    topic_id = topic_res.data[0]['id']
                    
                    # Mapping Logic
                    t_normalized = t.lower().strip()
                    
                    mapping_status = 'UNMAPPED'
                    mapping_method = None
                    confidence = 0.0
                    mapped_skill_id = None
                    
                    # Exact Match
                    if t_normalized in canonical_skills_map:
                        mapping_status = 'CONFIRMED'
                        mapping_method = 'EXACT_MATCH'
                        confidence = 1.0
                        mapped_skill_id = canonical_skills_map[t_normalized]['id']
                        confirmed += 1
                        skills_mapped += 1
                    else:
                        # LLM Proposed Match
                        llm_result = await map_topic_to_skill_llm(t, canonical_skills_names)
                        if llm_result.mapped_skill and llm_result.mapped_skill in name_to_id_map:
                            mapped_skill_id = name_to_id_map[llm_result.mapped_skill]
                            confidence = llm_result.confidence
                            mapping_method = 'LLM_PROPOSED'
                            
                            if confidence >= 0.8:
                                mapping_status = 'PROPOSED'
                                proposed += 1
                                skills_mapped += 1
                            else:
                                mapping_status = 'AMBIGUOUS'
                                ambiguous += 1
                        else:
                            mapping_status = 'UNMAPPED'
                            mapping_method = 'LLM_PROPOSED'
                            unmapped += 1
                            
                    # Insert Mapping
                    db.table('topic_skill_mappings').insert({
                        'topic_id': topic_id,
                        'skill_id': mapped_skill_id,
                        'mapping_status': mapping_status,
                        'mapping_method': mapping_method,
                        'confidence': confidence,
                        'source': source,
                        'source_page': source_page
                    }).execute()
                    
                    # If confirmed or proposed, add to course coverage!
                    if mapping_status in ('CONFIRMED', 'PROPOSED') and mapped_skill_id:
                        db.table('course_skills').upsert({
                            'course_id': course_id,
                            'skill_id': mapped_skill_id,
                            'coverage_level': 'COVERED',
                            'source_url': source_doc
                        }).execute()
                        
                    # Small sleep to prevent rate limiting
                    await asyncio.sleep(1)
        
        # Update raw extraction status
        db.table('raw_curriculum_extractions').update({'status': 'MAPPED'}).eq('id', raw['id']).execute()

    print("\n--- SKILL MAPPING COMPLETE ---")
    print(f"1. Number of curriculum topics processed: {topics_processed}")
    print(f"2. Number of skills mapped: {skills_mapped}")
    print(f"3. Confirmed mappings: {confirmed}")
    print(f"4. Proposed mappings: {proposed}")
    print(f"5. Ambiguous mappings: {ambiguous}")
    print(f"6. Unmapped topics: {unmapped}")
    print(f"7. Coverage statistics updated in course_skills.")
    print(f"8. Database tables created/modified: course_topics, topic_skill_mappings")

if __name__ == "__main__":
    asyncio.run(run_skill_mapping())
