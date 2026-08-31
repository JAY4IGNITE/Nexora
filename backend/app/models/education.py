from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID

class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    provider_id: Optional[UUID] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    mode: Optional[str] = None
    status: str = 'ACTIVE'

class Course(CourseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class CurriculumBase(BaseModel):
    institution_id: UUID
    program_name: str
    department: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None

class Curriculum(CurriculumBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
