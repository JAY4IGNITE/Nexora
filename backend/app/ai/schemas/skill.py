from pydantic import BaseModel, Field
from typing import List, Literal
from app.ai.schemas.base import AIResponse

class ExtractedSkill(BaseModel):
    name: str = Field(description="The canonical name of the skill mapped from the text.")
    proficiency: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"] = Field(
        description="Estimated proficiency based purely on evidence."
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this extraction and mapping.")
    evidence_quote: str = Field(description="Exact quote from the text that proves this skill.")

class StudentSkillExtraction(BaseModel):
    skills: List[ExtractedSkill] = Field(description="List of all unique canonical skills found in the text.")

class SkillExtractionResponse(AIResponse[StudentSkillExtraction]):
    pass
