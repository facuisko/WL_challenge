"""
Estado enriquecido para sistema agéntico
"""
from typing import TypedDict, List, Dict, Any, Optional

class AgenticResearchState(TypedDict):
    """Estado principal del workflow agéntico de investigación"""
    
    # Input del usuario
    user_query: str
    
    # Esquema de investigación propuesto
    proposed_outline: str
    outline_approved: bool
    outline_items: List[str]
    user_feedback: str
    
    # Estado agéntico avanzado
    current_research_topic: str
    research_context: Dict[str, Any]
    agent_decisions: Dict[str, Any]
    autonomous_actions: List[Dict[str, Any]]
    quality_assessments: Dict[str, float]
    inter_agent_messages: List[Dict[str, str]]
    
    # Control de flujo inteligente
    current_agent: str
    next_action: str
    supervisor_reasoning: str
    strategic_context: Dict[str, Any]
    
    # Resultados enriquecidos
    research_results: Dict[str, Any]
    analysis_complete: bool
    final_report: str
    
    # Metadatos
    step_count: int
    conversation_history: List[Dict[str, str]] 