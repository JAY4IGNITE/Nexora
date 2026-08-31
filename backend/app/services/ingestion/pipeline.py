import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from supabase import Client
from app.models.ingestion import RawJobRecord
from app.services.ingestion.provider import JobDataProvider
from app.services.ingestion.ai import LLMExtractionService

logger = logging.getLogger(__name__)

class PipelineEngine:
    def __init__(self, db: Client, provider: JobDataProvider):
        self.db = db
        self.provider = provider
        self.ai = LLMExtractionService()
        
        # Caching DB taxonomy in memory to avoid N+1 queries during the run
        self.canonical_roles = {}
        self.canonical_skills = {}
        self.canonical_locations = {}
        self._load_taxonomy()
        
    def _load_taxonomy(self):
        """Loads canonical roles, skills, and districts into memory."""
        try:
            roles = self.db.table('job_roles').select('id, name').execute()
            self.canonical_roles = {r['name'].lower(): r['id'] for r in roles.data}
            
            skills = self.db.table('skills').select('id, name').execute()
            self.canonical_skills = {s['name'].lower(): s['id'] for s in skills.data}
            
            districts = self.db.table('districts').select('id, name').execute()
            self.canonical_locations = {d['name'].lower(): d['id'] for d in districts.data}
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")

    def clean_text(self, text: str) -> str:
        """Removes excess whitespace and sanitizes text."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def _normalize_employment_type(self, emp_type: str) -> str:
        """Normalizes employment types to canonical ENUM-like strings."""
        if not emp_type:
            return "OTHER"
        emp_type = emp_type.upper().replace('-', '_').replace(' ', '_')
        if "FULL" in emp_type: return "FULL_TIME"
        if "PART" in emp_type: return "PART_TIME"
        if "CONTRACT" in emp_type: return "CONTRACT"
        if "INTERN" in emp_type: return "INTERNSHIP"
        return "OTHER"

    def run(self) -> Dict[str, Any]:
        """Executes the ingestion pipeline."""
        
        # 1. Create Ingestion Run Record
        run_record = self.db.table('job_ingestion_runs').insert({
            'provider': self.provider.get_provider_name(),
            'status': 'RUNNING'
        }).execute().data[0]
        run_id = run_record['id']
        
        metrics = {
            "records_received": 0,
            "records_valid": 0,
            "records_rejected": 0,
            "records_duplicate": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "records_failed": 0
        }
        
        try:
            for raw_job in self.provider.fetch_jobs():
                metrics["records_received"] += 1
                
                # 2. Validation & Cleaning
                title = self.clean_text(raw_job.title)
                if not title:
                    metrics["records_rejected"] += 1
                    continue
                    
                employer = self.clean_text(raw_job.employer)
                
                # 3. Deduplication Check (Idempotency)
                existing = self.db.table('job_postings').select('id').eq('source', raw_job.source).eq('source_url', raw_job.source_url if raw_job.source_url else f"{raw_job.source}-{raw_job.source_job_id}").execute()
                if existing.data:
                    metrics["records_duplicate"] += 1
                    continue
                    
                metrics["records_valid"] += 1
                
                # 4. Location Normalization
                district_id = None
                if raw_job.district:
                    cleaned_district = self.clean_text(raw_job.district).lower()
                    district_id = self.canonical_locations.get(cleaned_district)
                    
                # 5. Job Role Normalization
                role_id = self.canonical_roles.get(title.lower())
                if not role_id:
                    # Fallback to LLM
                    mapped_name = self.ai.normalize_job_role(title, list(self.canonical_roles.keys()))
                    if mapped_name and mapped_name.lower() in self.canonical_roles:
                        role_id = self.canonical_roles[mapped_name.lower()]
                
                # 6. Skill Extraction (Deterministic + AI)
                extracted_skill_ids = set()
                description = self.clean_text(raw_job.description)
                
                # Deterministic check
                desc_lower = description.lower()
                for skill_name, s_id in self.canonical_skills.items():
                    if f" {skill_name} " in f" {desc_lower} ":
                        extracted_skill_ids.add((s_id, 'EXACT_MATCH'))
                        
                # AI Semantic check (for implicit skills)
                if self.ai.enabled:
                    ai_skills = self.ai.extract_implicit_skills(description, list(self.canonical_skills.keys()))
                    for ai_skill in ai_skills:
                        s_id = self.canonical_skills.get(ai_skill.lower())
                        if s_id:
                            extracted_skill_ids.add((s_id, 'LLM_EXTRACTION'))
                
                # 7. Persistence
                emp_type = self._normalize_employment_type(raw_job.employment_type)
                source_url_hash = raw_job.source_url if raw_job.source_url else f"{raw_job.source}-{raw_job.source_job_id}"
                
                try:
                    # Insert Job Posting
                    posting = self.db.table('job_postings').insert({
                        'title': title,
                        'job_role_id': role_id, # Nullable if unresolved
                        'district_id': district_id,
                        'description': description,
                        'experience_requirements': raw_job.experience_requirement,
                        'education_requirements': raw_job.education_requirement,
                        'source': raw_job.source,
                        'source_url': source_url_hash, # Using as unique constraint fallback
                    }).execute().data[0]
                    
                    posting_id = posting['id']
                    
                    # Insert Skills
                    skill_inserts = [
                        {
                            'job_posting_id': posting_id,
                            'skill_id': sid,
                            'extraction_method': method,
                            'confidence': 0.95 if method == 'EXACT_MATCH' else 0.80
                        }
                        for sid, method in extracted_skill_ids
                    ]
                    
                    if skill_inserts:
                        self.db.table('job_posting_skills').insert(skill_inserts).execute()
                        
                    metrics["records_inserted"] += 1
                except Exception as e:
                    logger.error(f"Failed to insert job {title}: {e}")
                    metrics["records_failed"] += 1

            # Finalize run
            self.db.table('job_ingestion_runs').update({
                'status': 'COMPLETED',
                'completed_at': datetime.utcnow().isoformat(),
                **metrics
            }).eq('id', run_id).execute()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Ingestion run failed: {e}")
            self.db.table('job_ingestion_runs').update({
                'status': 'FAILED',
                'completed_at': datetime.utcnow().isoformat(),
                **metrics
            }).eq('id', run_id).execute()
            raise e
