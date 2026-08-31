from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GOVERNMENT = "GOVERNMENT"
    INSTITUTION = "INSTITUTION"
    TRAINER = "TRAINER"
    EMPLOYER = "EMPLOYER"
    STUDENT = "STUDENT"

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    is_active: bool = True

class UserCreate(UserBase):
    firebase_uid: str

class UserInDB(UserBase):
    id: UUID
    firebase_uid: str
    created_at: datetime
    updated_at: datetime

class User(UserInDB):
    pass
