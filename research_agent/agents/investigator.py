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
        self._openai_client = None
    
    @property
    def openai_client(self):
        """Lazy loading del cliente OpenAI"""
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client
    
    def generate_research_outline(self, state: ResearchState) -> ResearchState:
        """Genera un esquema de investigación con 6 opciones simples"""
        user_query = state['user_query']
        user_feedback = state.get('user_feedback', '')
        existing_items = state.get('outline_items', [])
        
        self.log(f"Analizando consulta: '{user_query}'")
        
        if user_feedback:
            self.log(f"Aplicando feedback del usuario: {user_feedback}")
        
        # Prompt simplificado para 6 opciones sin subtemas
        if user_feedback and existing_items:
            prompt = f"""
            El usuario ha dado feedback sobre el esquema anterior. Genera un nuevo esquema incorporando sus cambios:
            
            CONSULTA ORIGINAL: {user_query}
            FEEDBACK DEL USUARIO: {user_feedback}
            ELEMENTOS ACTUALES: {existing_items}
            
            Genera exactamente 6 elementos principales de investigación (sin subtemas).
            Si hay elementos aprobados por el usuario, inclúyelos y completa hasta 6 elementos.
            Si hay más de 6 elementos aprobados, selecciona los 6 más relevantes.
            
            Formato de respuesta:
            ## ESQUEMA DE INVESTIGACIÓN
            
            ### 1. [Elemento 1]
            ### 2. [Elemento 2]
            ### 3. [Elemento 3]
            ### 4. [Elemento 4]
            ### 5. [Elemento 5]
            ### 6. [Elemento 6]
            
            Solo títulos principales, sin subtemas ni detalles adicionales.
            """
        else:
            prompt = f"""
            Como experto investigador, crea un esquema de investigación para:
            
            CONSULTA: {user_query}
            
            Genera exactamente 6 elementos principales de investigación (sin subtemas).
            Cada elemento debe ser un aspecto importante y específico del tema.
            
            Formato de respuesta:
            ## ESQUEMA DE INVESTIGACIÓN
            
            ### 1. [Elemento 1]
            ### 2. [Elemento 2]
            ### 3. [Elemento 3]
            ### 4. [Elemento 4]
            ### 5. [Elemento 5]
            ### 6. [Elemento 6]
            
            Solo títulos principales, sin subtemas ni detalles adicionales.
            Sé específico y enfócate en información actual y relevante.
            """
        
        try:
            outline = self.openai_client.generate_response(prompt)
            self.log("✅ Esquema de investigación generado")
            
            return {
                **state,
                "current_agent": self.name,
                "proposed_outline": outline,
                "user_feedback": "",
            }
            
        except Exception as e:
            self.log(f"❌ Error generando esquema: {e}")
            # Fallback con esquema básico
            fallback_outline = self._generate_fallback_outline(user_query)
            return {
                **state,
                "current_agent": self.name,
                "proposed_outline": fallback_outline,
                "user_feedback": "",
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
        
        ### 1. Introducción y Contexto de {query}
        ### 2. Aspectos Técnicos y Tecnológicos
        ### 3. Aplicaciones Prácticas y Casos de Uso
        ### 4. Tendencias Actuales y Desarrollos Recientes
        ### 5. Desafíos y Limitaciones
        ### 6. Futuro y Proyecciones
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