from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class AIResponse(BaseModel, Generic[T]):
    """Standardized structured output for all AI Agent responses."""
    result: T = Field(description="The core output payload requested from the agent.")
    reasoning_summary: str = Field(description="A brief explanation of how the AI arrived at this result.")
    confidence: float = Field(ge=0.0, le=1.0, description="The model's confidence in this result (0.0 to 1.0).")
    evidence: List[str] = Field(default_factory=list, description="List of factual references or database IDs supporting this result.")
    limitations: List[str] = Field(default_factory=list, description="Any assumptions or limitations in the AI's response.")
