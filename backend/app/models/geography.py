from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class StateBase(BaseModel):
    name: str
    code: Optional[str] = None

class State(StateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class DistrictBase(BaseModel):
    state_id: UUID
    name: str
    code: Optional[str] = None

class District(DistrictBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
