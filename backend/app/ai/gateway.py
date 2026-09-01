import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.ai.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class AIGateway:
    """Service layer between Agents and the Gemini Client."""
    
    def __init__(self):
        # Lazy load the client to avoid failing application startup if key is missing
        self._client: Optional[GeminiClient] = None
        
    @property
    def client(self) -> GeminiClient:
        if not self._client:
            self._client = GeminiClient()
        return self._client
        
    async def request_structured_generation(
        self,
        agent_name: str,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0
    ) -> T:
        """
        Routes the request to the client, handling logging and cross-cutting concerns.
        """
        logger.info(f"Agent '{agent_name}' requesting structured generation.")
        try:
            result = await self.client.generate_structured(
                prompt=prompt,
                response_schema=response_schema,
                system_instruction=system_instruction,
                temperature=temperature
            )
            logger.info(f"Agent '{agent_name}' generation successful.")
            return result
        except Exception as e:
            logger.error(f"Agent '{agent_name}' generation failed: {str(e)}")
            raise

# Singleton instance for dependency injection
ai_gateway = AIGateway()
