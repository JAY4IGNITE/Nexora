from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class RawJobRecord(BaseModel):
    source: str
    source_job_id: str
    source_url: Optional[str] = None
    title: str
    employer: str
    description: str
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    employment_type: Optional[str] = None
    experience_requirement: Optional[str] = None
    education_requirement: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    contract_type: Optional[str] = None
    contract_time: Optional[str] = None
    posted_at: Optional[datetime] = None
    collected_at: datetime
    skills: List[str] = []
    
    model_config = {
        "extra": "ignore"
    }
