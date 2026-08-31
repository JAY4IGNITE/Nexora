from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class SkillRelationshipType(str, Enum):
    PREREQUISITE = "PREREQUISITE"
    RELATED_TO = "RELATED_TO"
    USED_WITH = "USED_WITH"
    COMPLEMENTARY = "COMPLEMENTARY"
    SUBSKILL = "SUBSKILL"

class SkillBase(BaseModel):
    name: str
    normalized_name: str
    category: Optional[str] = None
    description: Optional[str] = None
    skill_type: Optional[str] = None

class Skill(SkillBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class JobRoleSkillBase(BaseModel):
    job_role_id: UUID
    skill_id: UUID
    importance: Optional[int] = None
    proficiency_level: Optional[str] = None
    evidence_source: Optional[str] = None

class JobRoleSkill(JobRoleSkillBase):
    created_at: datetime
