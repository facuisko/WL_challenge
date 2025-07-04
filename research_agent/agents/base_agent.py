"""
Clase base para todos los agentes
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from research_agent.models.state import ResearchState
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.config.settings import Settings

class BaseAgent(ABC):
    """Clase base para agentes"""
    
    def __init__(self, name: str):
        self.name = name
        self.settings = Settings()
    
    @abstractmethod
    def execute(self, state: Union[ResearchState, AgenticResearchState]) -> Union[ResearchState, AgenticResearchState]:
        """Ejecuta la lógica principal del agente"""
        pass
    
    def log(self, message: str, emoji: str = "🤖"):
        """Log con formato consistente"""
        print(f"{emoji} {self.name.upper()}: {message}") 