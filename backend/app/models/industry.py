from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class SectorBase(BaseModel):
    name: str
    description: Optional[str] = None

class Sector(SectorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class JobRoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    sector_id: Optional[UUID] = None

class JobRole(JobRoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class JobPostingBase(BaseModel):
    title: str
    job_role_id: Optional[UUID] = None
    employer_id: Optional[UUID] = None
    sector_id: Optional[UUID] = None
    district_id: Optional[UUID] = None
    description: Optional[str] = None
    experience_requirements: Optional[str] = None
    education_requirements: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None

class JobPosting(JobPostingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
