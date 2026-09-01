import logging
from typing import Dict, Type
from app.ai.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Central registry for discovering and instantiating AI Agents."""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        """Registers an agent class."""
        name = agent_class.__name__
        cls._agents[name] = agent_class
        logger.info(f"Registered Agent: {name}")
        
    @classmethod
    def get_agent(cls, name: str) -> BaseAgent:
        """Instantiates and returns the requested agent."""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return cls._agents[name]()

def register_agent(cls):
    """Decorator to easily register agents."""
    AgentRegistry.register(cls)
    return cls
