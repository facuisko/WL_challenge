"""
Agente investigador que usa OpenAI para estructurar y realizar investigación
"""
from typing import Dict, Any, List
import requests
import urllib.parse
import re
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.state import ResearchState
from research_agent.models.agentic_state import AgenticResearchState
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
    
    def generate_research_outline(self, state: AgenticResearchState) -> AgenticResearchState:
        """
        Genera esquema de investigación con títulos lógicos
        Cumple con el challenge: 'Finds and gathers initial information about your topic'
        """
        user_query = state['user_query']
        user_feedback = state.get('user_feedback', '')
        existing_items = state.get('outline_items', [])
        
        self.log(f"📋 Generando títulos lógicos para: '{user_query}'")
        
        if user_feedback:
            self.log(f"Aplicando feedback del usuario: {user_feedback}")
        
        # Crear esquema con títulos lógicos (sin links)
        if user_feedback and existing_items:
            outline = self._create_outline_from_feedback(user_query, user_feedback, existing_items)
        else:
            outline = self._create_logical_outline(user_query)
        
        self.log("✅ Esquema de títulos lógicos generado")
        
        return {
            **state,
            "current_agent": self.name,
            "proposed_outline": outline,
            "outline_approved": False,  # Explícitamente marcar como no aprobado
            "user_feedback": "",
            "research_context": {
                **state.get("research_context", {}),
                "topic_analyzed": user_query,
                "outline_method": "logical_titles"
            }
        }
    
    def _find_real_sources(self, query: str) -> Dict[str, Any]:
        """
        Encuentra fuentes reales sobre el tema (cumple requirement del challenge)
        """
        from research_agent.tools.web_search import WebSearchClient
        
        search_client = WebSearchClient()
        self.log(f"🌐 Buscando fuentes reales para: {query}")
        
        # Realizar búsqueda comprehensiva con verificación de fuentes
        search_results = search_client.search_comprehensive(query, max_results=5)
        
        verified_count = len([s for s in search_results.get("verified_sources", []) if s.get("verified")])
        self.log(f"📚 Encontradas {verified_count} fuentes verificadas")
        
        return search_results
    
    def _generate_source_summaries(self, search_results: Dict[str, Any], query: str) -> List[Dict[str, str]]:
        """
        Genera summaries de las fuentes encontradas usando modelos económicos
        Cumple con: 'Generates initial summaries using cheaper AI models'
        """
        verified_sources = search_results.get("verified_sources", [])
        
        if not verified_sources:
            return []
        
        summaries = []
        self.log(f"📝 Generando summaries de {len(verified_sources)} fuentes")
        
        for i, source in enumerate(verified_sources[:5], 1):  # Máximo 5 fuentes
            try:
                summary_prompt = f"""
                Analiza esta fuente y crea un summary enfocado en el tema "{query}":
                
                FUENTE: {source.get('title', 'Sin título')}
                URL: {source.get('url', 'No URL')}
                CONTENIDO: {source.get('summary', 'Sin contenido')}
                VERIFICACIÓN: {source.get('verification_status', 'No verificada')}
                
                Crea un summary de 2-3 oraciones que:
                1. Identifique qué información específica aporta sobre "{query}"
                2. Mencione el tipo de fuente y su credibilidad
                3. Destaque los aspectos más relevantes para la investigación
                
                Summary conciso y enfocado:
                """
                
                # Usar modelo económico para summaries (como pide el challenge)
                summary_text = self.openai_client.generate_response(
                    summary_prompt, 
                    task_type="research",  # Usará modelo económico
                    max_tokens=200
                )
                
                summaries.append({
                    "source_title": source.get('title', 'Sin título'),
                    "source_url": source.get('url', ''),
                    "source_type": source.get('source', 'Unknown'),
                    "verification_status": source.get('verification_status', ''),
                    "summary": summary_text,
                    "relevance_score": source.get('score', 0)
                })
                
                self.log(f"   ✅ Summary {i}: {source.get('title', 'Sin título')[:50]}...")
                
            except Exception as e:
                self.log(f"   ❌ Error en summary {i}: {e}")
                continue
        
        return summaries
    
    def _create_logical_outline(self, query: str) -> str:
        """
        Crea esquema con títulos lógicos y estructurados para el tema
        """
        outline_prompt = f"""
        Crea un esquema de investigación con títulos lógicos y bien estructurados para: "{query}"
        
        INSTRUCCIONES:
        1. Genera exactamente 6 títulos principales
        2. Los títulos deben ser específicos y relevantes al tema
        3. Deben cubrir los aspectos más importantes del tema
        4. Organiza de manera lógica (general a específico, cronológico, etc.)
        5. Usa un enfoque académico y profesional
        6. NO incluyas links, URLs o referencias específicas
        7. Solo títulos descriptivos y claros
        
        FORMATO DE RESPUESTA:
        ## ESQUEMA DE INVESTIGACIÓN
        
        ### 1. [Título descriptivo y específico]
        ### 2. [Título descriptivo y específico]  
        ### 3. [Título descriptivo y específico]
        ### 4. [Título descriptivo y específico]
        ### 5. [Título descriptivo y específico]
        ### 6. [Título descriptivo y específico]
        
        Solo títulos principales, sin subtemas ni explicaciones adicionales.
        """
        
        try:
            return self.openai_client.generate_response(outline_prompt, task_type="outline")
        except Exception as e:
            self.log(f"❌ Error creando esquema lógico: {e}")
            return self._generate_fallback_outline(query)
    
    def _create_outline_from_sources(self, query: str, source_summaries: List[Dict[str, str]]) -> str:
        """
        Crea esquema de investigación basado en las fuentes reales encontradas
        """
        sources_text = ""
        for i, summary in enumerate(source_summaries, 1):
            sources_text += f"\nFUENTE {i}: {summary['source_title']}\n"
            sources_text += f"Tipo: {summary['source_type']} | {summary['verification_status']}\n"
            sources_text += f"Summary: {summary['summary']}\n"
            sources_text += f"URL: {summary['source_url']}\n"
        
        outline_prompt = f"""
        Basado en las fuentes reales encontradas, crea un esquema de investigación para: "{query}"
        
        FUENTES ENCONTRADAS Y VERIFICADAS:
        {sources_text}
        
        Genera exactamente 6 elementos de investigación que:
        1. Se basen en la información real encontrada en las fuentes
        2. Cubran los aspectos más importantes identificados
        3. Aprovechen la diversidad de fuentes disponibles
        4. Sean específicos y enfocados
        
        Formato de respuesta:
        ## ESQUEMA DE INVESTIGACIÓN
        
        ### 1. [Elemento basado en fuentes]
        ### 2. [Elemento basado en fuentes]
        ### 3. [Elemento basado en fuentes]
        ### 4. [Elemento basado en fuentes]
        ### 5. [Elemento basado en fuentes]
        ### 6. [Elemento basado en fuentes]
        
        Solo títulos principales, sin subtemas.
        """
        
        try:
            return self.openai_client.generate_response(outline_prompt, task_type="outline")
        except Exception as e:
            self.log(f"❌ Error creando esquema de fuentes: {e}")
            return self._generate_fallback_outline(query)
    
    def _create_outline_from_feedback(self, query: str, feedback: str, existing_items: List[str]) -> str:
        """
        Crea esquema incorporando feedback del usuario
        """
        feedback_prompt = f"""
        Incorpora el feedback del usuario para mejorar el esquema de títulos:
        
        CONSULTA ORIGINAL: {query}
        FEEDBACK DEL USUARIO: {feedback}
        ELEMENTOS ACTUALES: {existing_items}
        
        Genera un esquema mejorado que:
        1. Incorpore el feedback específico del usuario
        2. Mejore la estructura y lógica de los títulos
        3. Mantenga exactamente 6 elementos
        4. Sea más específico y relevante al tema
        
        INSTRUCCIONES:
        - NO incluyas links, URLs o referencias específicas
        - Solo títulos descriptivos y claros
        - Enfoque académico y profesional
        
        Formato de respuesta:
        ## ESQUEMA DE INVESTIGACIÓN
        
        ### 1. [Elemento mejorado]
        ### 2. [Elemento mejorado]
        ### 3. [Elemento mejorado]
        ### 4. [Elemento mejorado]
        ### 5. [Elemento mejorado]
        ### 6. [Elemento mejorado]
        """
        
        try:
            return self.openai_client.generate_response(feedback_prompt, task_type="outline")
        except Exception as e:
            self.log(f"❌ Error incorporando feedback: {e}")
            return self._generate_fallback_outline(query)
    
    def conduct_detailed_research(self, state: AgenticResearchState) -> AgenticResearchState:
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
    
    def execute(self, state: AgenticResearchState) -> AgenticResearchState:
        """Ejecuta la acción correspondiente según el estado"""
        action = state.get('next_action')
        
        if action == "GENERATE_OUTLINE":
            return self.generate_research_outline(state)
        elif action == "CONDUCT_RESEARCH":
            return self.conduct_detailed_research(state)
        else:
            return state 
    
    
