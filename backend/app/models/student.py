from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum

class StudentProfileBase(BaseModel):
    institution_id: Optional[UUID] = None
    program: Optional[str] = None
    graduation_year: Optional[int] = None
    district_id: Optional[UUID] = None

class StudentProfile(StudentProfileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class StudentSkillBase(BaseModel):
    student_id: UUID
    skill_id: UUID
    proficiency: Optional[int] = None
    confidence: Optional[float] = None
    source: Optional[str] = None
    verified_status: bool = False
    last_assessed: Optional[datetime] = None

class StudentSkill(StudentSkillBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class SkillGapBase(BaseModel):
    student_id: UUID
    target_role_id: UUID
    skill_id: UUID
    required_proficiency: Optional[int] = None
    current_proficiency: Optional[int] = None
    gap_severity: Optional[str] = None
    status: str = 'OPEN'

class SkillGap(SkillGapBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
