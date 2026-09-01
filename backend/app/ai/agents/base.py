import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Any
from pydantic import BaseModel

from app.ai.gateway import ai_gateway
from app.ai.schemas.base import AIResponse

logger = logging.getLogger(__name__)

InputType = TypeVar('InputType')

class BaseAgent(ABC):
    """Abstract base class for all Nexora AI Agents."""
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Name of the agent for logging and registry."""
        pass
        
    @property
    @abstractmethod
    def response_schema(self) -> Type[BaseModel]:
        """The specific Pydantic schema this agent returns (should subclass AIResponse)."""
        pass
        
    @property
    def system_instruction(self) -> str:
        """Optional system instruction to pass to the model."""
        return "You are an expert AI agent working within the Nexora system."
        
    @abstractmethod
    async def validate_input(self, input_data: InputType) -> None:
        """Validates the input parameters before processing."""
        pass
        
    @abstractmethod
    async def build_context(self, input_data: InputType) -> Any:
        """Fetches necessary evidence/context from external services (e.g., DB)."""
        pass
        
    @abstractmethod
    def build_prompt(self, input_data: InputType, context: Any) -> str:
        """Constructs the prompt string to send to Gemini."""
        pass
        
    def parse_output(self, raw_output: BaseModel) -> BaseModel:
        """Optional hook to further parse or validate the structured output."""
        return raw_output
        
    async def run(self, input_data: InputType) -> BaseModel:
        """
        The main lifecycle method. Orchestrates validation, context gathering,
        prompt building, AI generation, and output parsing.
        """
        logger.info(f"Agent '{self.agent_name}' starting run.")
        
        await self.validate_input(input_data)
        context = await self.build_context(input_data)
        prompt = self.build_prompt(input_data, context)
        
        raw_output = await ai_gateway.request_structured_generation(
            agent_name=self.agent_name,
            prompt=prompt,
            response_schema=self.response_schema,
            system_instruction=self.system_instruction
        )
        
        parsed = self.parse_output(raw_output)
        logger.info(f"Agent '{self.agent_name}' completed run.")
        return parsed
