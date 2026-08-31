import os
import json
import logging
from typing import Optional, Dict, List
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class LLMExtractionService:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        self.enabled = bool(api_key)
        if self.enabled:
            self.client = genai.Client(api_key=api_key)
        else:
            logger.warning("GEMINI_API_KEY not found. LLM Extraction Service is disabled.")
            self.client = None

    def normalize_job_role(self, raw_title: str, available_roles: List[str]) -> Optional[str]:
        """
        Given a raw job title and a list of canonical roles, 
        returns the closest canonical role, or None if no match is confident.
        """
        if not self.enabled:
            return None
            
        prompt = f"""
        You are an AI career intelligence system. 
        Map the raw job title: "{raw_title}" to the closest canonical role from this list:
        {json.dumps(available_roles)}
        
        If none of the roles are a good match, return null.
        Respond ONLY with a JSON object in this format:
        {{"mapped_role": "Canonical Role Name" | null}}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            result = json.loads(response.text)
            return result.get("mapped_role")
        except Exception as e:
            logger.error(f"LLM Role Normalization failed for {raw_title}: {e}")
            return None

    def extract_implicit_skills(self, description: str, canonical_skills: List[str]) -> List[str]:
        """
        Analyzes a job description to extract skills that match our canonical list.
        Useful for implicit soft skills or differently phrased requirements.
        """
        if not self.enabled:
            return []
            
        prompt = f"""
        Extract all professional skills mentioned or heavily implied in this job description.
        Only return skills that exist in this canonical list:
        {json.dumps(canonical_skills)}
        
        Job Description:
        {description}
        
        Respond ONLY with a JSON object in this format:
        {{"skills": ["Skill 1", "Skill 2"]}}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            result = json.loads(response.text)
            return result.get("skills", [])
        except Exception as e:
            logger.error(f"LLM Skill Extraction failed: {e}")
            return []
