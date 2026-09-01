import logging
from typing import List, Type
from pydantic import BaseModel
from app.ai.agents.base import BaseAgent
from app.ai.agents.registry import register_agent
from app.ai.schemas.skill import SkillExtractionResponse
from app.services.database import get_supabase_client

logger = logging.getLogger(__name__)

class SkillAgentInput(BaseModel):
    text: str

@register_agent
class SkillIntelligenceAgent(BaseAgent):
    
    @property
    def agent_name(self) -> str:
        return "SkillIntelligenceAgent"
        
    @property
    def response_schema(self) -> Type[BaseModel]:
        return SkillExtractionResponse
        
    @property
    def system_instruction(self) -> str:
        return (
            "You are an expert technical recruiter and AI system responsible for extracting "
            "factual skills from a student's resume or project description.\n"
            "Rules:\n"
            "1. ONLY map extracted skills to the provided list of Canonical Skills.\n"
            "2. Do NOT invent new skills or use terminology outside the canonical list. Ignore skills not in the list.\n"
            "3. Proficiency Scoring:\n"
            "   - BEGINNER: Mentioned in a list of skills, course, or basic familiarity.\n"
            "   - INTERMEDIATE: Used in a project, internship, or practical application.\n"
            "   - ADVANCED: Used extensively across multiple complex projects, lead a team using it, or has deep specialization.\n"
            "4. Provide exact quotes as evidence."
        )
        
    async def validate_input(self, input_data: SkillAgentInput) -> None:
        if not input_data.text or len(input_data.text.strip()) == 0:
            raise ValueError("Input text cannot be empty.")
            
    async def build_context(self, input_data: SkillAgentInput) -> List[str]:
        """Fetches existing canonical skills from Supabase."""
        try:
            supabase = get_supabase_client()
            response = supabase.table("skills").select("name").execute()
            if response.data:
                return [row["name"] for row in response.data]
            return []
        except Exception as e:
            logger.error(f"Failed to fetch canonical skills: {e}")
            return []
            
    def build_prompt(self, input_data: SkillAgentInput, context: List[str]) -> str:
        canonical_list = ", ".join(context) if context else "None provided"
        return (
            f"Here is the list of ALLOWED canonical skills:\n[{canonical_list}]\n\n"
            "Extract skills from the following student text and map them strictly to the canonical skills.\n"
            "Determine the proficiency based on how the skill is used in the text.\n\n"
            f"STUDENT TEXT:\n{input_data.text}"
        )
