import json
import logging
import asyncio
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.ai.exceptions import AIConfigError, AIClientError, AIRetryExhaustedError, AIParseError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise AIConfigError("GEMINI_API_KEY is not configured in the environment.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 3,
        base_delay: float = 2.0
    ) -> T:
        """Generates a structured Pydantic model from Gemini with retry logic."""
        config_kwargs = {
            "response_mime_type": "application/json",
            "response_schema": response_schema,
            "temperature": temperature
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
            
        config = types.GenerateContentConfig(**config_kwargs)
        
        for attempt in range(max_retries):
            try:
                # Offload synchronous generate_content to threadpool to avoid blocking event loop
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                
                if not response.text:
                    raise AIParseError("Received empty response from Gemini.")
                    
                data = json.loads(response.text)
                return response_schema(**data)
                
            except APIError as e:
                # Catch rate limits or 5xx errors
                if e.code == 429 or e.code >= 500:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Gemini API Error {e.code}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                raise AIClientError(f"Gemini API Error: {e.message}") from e
            except json.JSONDecodeError as e:
                raise AIParseError(f"Failed to parse JSON response: {e}") from e
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Unexpected error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                raise AIClientError(f"Unexpected error during generation: {e}") from e
                
        raise AIRetryExhaustedError(f"Failed to generate content after {max_retries} attempts.")
