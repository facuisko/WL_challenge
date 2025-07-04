"""
Configuración del sistema
"""
import os
from typing import Optional

class Settings:
    """Configuración centralizada"""
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4"
    
    # Tavily Web Search
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Configuración de agentes
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida que la configuración sea correcta"""
        if not cls.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY no configurado")
            print("💡 Configuralo con: export OPENAI_API_KEY='tu-key'")
            return False
        return True 