"""
Agente investigador que usa OpenAI para estructurar y realizar investigación
"""
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.state import ResearchState
from research_agent.tools.openai_client import OpenAIClient

class InvestigatorAgent(BaseAgent):
    """Agente investigador inteligente"""
    
    def __init__(self):
        super().__init__("Investigador")
        self.openai_client = OpenAIClient()
    
    def generate_research_outline(self, state: ResearchState) -> ResearchState:
        """Genera un esquema de investigación estructurado"""
        user_query = state['user_query']
        
        self.log(f"Analizando consulta: '{user_query}'")
        self.log("Generando esquema de investigación...")
        
        # Prompt para generar esquema
        prompt = f"""
        Como experto investigador, analiza esta consulta y crea un esquema detallado de investigación:
        
        CONSULTA: {user_query}
        
        Genera un esquema estructurado que incluya:
        1. Aspectos principales a investigar (3-5 temas)
        2. Subtemas específicos para cada aspecto
        3. Fuentes sugeridas de información
        4. Preguntas clave a responder
        
        Formato de respuesta:
        ## ESQUEMA DE INVESTIGACIÓN
        
        ### 1. [Aspecto Principal 1]
        - Subtema A
        - Subtema B
        - Fuentes: [tipos de fuentes]
        - Preguntas clave: [2-3 preguntas]
        
        ### 2. [Aspecto Principal 2]
        ...
        
        Sé específico y enfócate en información actual y relevante.
        """
        
        try:
            outline = self.openai_client.generate_response(prompt)
            self.log("✅ Esquema de investigación generado")
            
            return {
                **state,
                "current_agent": self.name,
                "proposed_outline": outline
            }
            
        except Exception as e:
            self.log(f"❌ Error generando esquema: {e}")
            # Fallback con esquema básico
            fallback_outline = self._generate_fallback_outline(user_query)
            return {
                **state,
                "current_agent": self.name,
                "proposed_outline": fallback_outline
            }
    
    def conduct_detailed_research(self, state: ResearchState) -> ResearchState:
        """Realiza investigación detallada basada en el esquema aprobado"""
        outline = state['proposed_outline']
        user_query = state['user_query']
        
        self.log("Realizando investigación detallada...")
        
        # Prompt para investigación detallada
        prompt = f"""
        Basado en este esquema de investigación aprobado, realiza una investigación detallada:
        
        CONSULTA ORIGINAL: {user_query}
        
        ESQUEMA APROBADO:
        {outline}
        
        Para cada sección del esquema, proporciona:
        1. Información detallada y actualizada
        2. Datos específicos, estadísticas si es relevante
        3. Tendencias actuales
        4. Ejemplos concretos
        5. Fuentes implícitas (sin URLs específicas)
        
        Genera un reporte completo y bien estructurado.
        """
        
        try:
            research_results = self.openai_client.generate_response(prompt)
            self.log("✅ Investigación detallada completada")
            
            return {
                **state,
                "current_agent": self.name,
                "research_results": {"detailed_research": research_results}
            }
            
        except Exception as e:
            self.log(f"❌ Error en investigación: {e}")
            return {
                **state,
                "current_agent": self.name,
                "research_results": {"error": "Error en investigación detallada"}
            }
    
    def _generate_fallback_outline(self, query: str) -> str:
        """Genera un esquema básico si falla OpenAI"""
        return f"""
        ## ESQUEMA DE INVESTIGACIÓN (Versión Básica)
        
        ### 1. Introducción y Contexto
        - Definiciones clave relacionadas con: {query}
        - Contexto actual del tema
        
        ### 2. Aspectos Técnicos
        - Desarrollos recientes
        - Tecnologías involucradas
        
        ### 3. Aplicaciones Prácticas
        - Casos de uso actuales
        - Ejemplos de implementación
        
        ### 4. Tendencias y Futuro
        - Proyecciones
        - Desafíos y oportunidades
        """
    
    def execute(self, state: ResearchState) -> ResearchState:
        """Ejecuta la acción correspondiente según el estado"""
        action = state.get('next_action')
        
        if action == "GENERATE_OUTLINE":
            return self.generate_research_outline(state)
        elif action == "CONDUCT_RESEARCH":
            return self.conduct_detailed_research(state)
        else:
            return state 