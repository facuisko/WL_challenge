"""
Estados compartidos del sistema
"""
from typing import TypedDict, List, Dict, Optional

class ResearchState(TypedDict):
    """Estado principal del workflow de investigación"""
    # Input del usuario
    user_query: str
    
    # Esquema de investigación propuesto
    proposed_outline: str
    outline_approved: bool
    
    # Control de flujo
    current_agent: str
    next_action: str
    
    # Resultados
    research_results: Dict[str, str]
    final_report: str
    
    # Metadatos
    step_count: int
    conversation_history: List[Dict[str, str]] 