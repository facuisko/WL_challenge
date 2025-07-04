"""
Agente curador que realiza análisis profundo del contenido
"""
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.tools.openai_client import OpenAIClient
from research_agent.tools.web_search import WebSearchClient
from typing import Dict, List, Any

class CuratorAgent(BaseAgent):
    """Agente curador que analiza y sintetiza información en profundidad"""
    
    def __init__(self):
        super().__init__("Curador")
        self._openai_client = None
        self._search_client = None
    
    @property
    def openai_client(self):
        """Lazy loading del cliente OpenAI"""
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client
    
    @property
    def search_client(self):
        """Lazy loading del cliente de búsqueda"""
        if self._search_client is None:
            self._search_client = WebSearchClient()
        return self._search_client
    
    def execute(self, state: AgenticResearchState) -> AgenticResearchState:
        """Ejecuta curación profunda del contenido aprobado"""
        action = state.get('next_action')
        
        if action == "CURATE_CONTENT":
            return self.curate_approved_content(state)
        else:
            return state
    
    def curate_approved_content(self, state: AgenticResearchState) -> AgenticResearchState:
        """
        Realiza curación profunda del contenido aprobado por el usuario
        """
        approved_items = state.get('outline_items', [])
        user_query = state['user_query']
        
        if not approved_items:
            self.log("❌ No hay elementos aprobados para curar")
            return {
                **state,
                "current_agent": self.name,
                "research_context": {"error": "No approved items to curate"}
            }
        
        self.log(f"🔍 Iniciando curación profunda de {len(approved_items)} elementos")
        
        # Realizar investigación detallada para cada elemento aprobado
        curated_content = {}
        research_context = {
            "total_items": len(approved_items),
            "completed_items": 0,
            "detailed_analysis": {},
            "web_sources": {},
            "synthesis_notes": []
        }
        
        for i, item in enumerate(approved_items, 1):
            self.log(f"📊 Curando elemento {i}/{len(approved_items)}: {item}")
            
            # Paso 1: Búsqueda web para este elemento específico
            search_query = f"{user_query} {item}"
            search_results = self.search_client.search_comprehensive(search_query, max_results=3)
            
            # Paso 2: Análisis profundo usando AI
            analysis = self._perform_deep_analysis(item, search_results, user_query)
            
            # Paso 3: Almacenar resultados
            curated_content[f"item_{i}"] = {
                "title": item,
                "analysis": analysis,
                "sources": search_results,
                "key_insights": self._extract_key_insights(analysis)
            }
            
            research_context["completed_items"] = i
            research_context["detailed_analysis"][item] = analysis
            research_context["web_sources"][item] = search_results["summary"]
        
        # Paso 4: Síntesis final de todo el contenido curado
        synthesis = self._synthesize_curated_content(curated_content, user_query)
        research_context["synthesis_notes"] = synthesis
        
        self.log("✅ Curación profunda completada")
        
        return {
            **state,
            "current_agent": self.name,
            "research_results": curated_content,
            "research_context": research_context,
            "analysis_complete": True
        }
    
    def _perform_deep_analysis(self, item: str, search_results: Dict[str, Any], 
                              original_query: str) -> str:
        """Realiza análisis profundo de un elemento específico"""
        
        # Preparar contenido de fuentes para el análisis
        sources_content = ""
        
        # Incluir resúmenes de Wikipedia
        for wiki_result in search_results.get("wikipedia", []):
            sources_content += f"\n**{wiki_result['title']}**: {wiki_result['summary']}\n"
        
        # Incluir resultados web
        for web_result in search_results.get("web", []):
            sources_content += f"\n**{web_result['title']}**: {web_result['summary']}\n"
        
        analysis_prompt = f"""
        Realiza un análisis profundo y estructurado del siguiente elemento de investigación:
        
        CONSULTA ORIGINAL: {original_query}
        ELEMENTO A ANALIZAR: {item}
        
        FUENTES ENCONTRADAS:
        {sources_content}
        
        INSTRUCCIONES:
        1. Analiza la información disponible sobre este elemento específico
        2. Identifica tendencias, patrones y desarrollos clave
        3. Extrae insights importantes y datos relevantes
        4. Considera el contexto de la consulta original
        5. Señala cualquier limitación o brecha en la información
        
        ESTRUCTURA DE RESPUESTA:
        ## Análisis de {item}
        
        ### Hallazgos Principales
        [Lista de hallazgos clave con datos específicos]
        
        ### Tendencias Identificadas
        [Tendencias actuales y proyecciones]
        
        ### Insights Críticos
        [Análisis profundo e interpretaciones]
        
        ### Datos y Estadísticas
        [Información cuantitativa relevante]
        
        ### Limitaciones
        [Qué información falta o es incierta]
        
        Mantén el análisis enfocado, objetivo y basado en evidencia.
        """
        
        try:
            analysis = self.openai_client.generate_response(
                analysis_prompt, 
                task_type="analysis",
                max_tokens=1500
            )
            return analysis
            
        except Exception as e:
            self.log(f"❌ Error en análisis profundo de '{item}': {e}")
            return f"Error al analizar {item}: {str(e)}"
    
    def _extract_key_insights(self, analysis: str) -> List[str]:
        """Extrae insights clave del análisis"""
        
        insight_prompt = f"""
        Del siguiente análisis, extrae los 3-5 insights más importantes y accionables:
        
        ANÁLISIS:
        {analysis}
        
        Extrae insights que sean:
        - Específicos y concretos
        - Relevantes para la investigación
        - Basados en evidencia
        - Accionables o informativos
        
        Responde solo con una lista numerada de insights, sin explicaciones adicionales.
        """
        
        try:
            insights_text = self.openai_client.generate_response(
                insight_prompt,
                task_type="analysis", 
                max_tokens=300
            )
            
            # Parsear insights en lista
            insights = []
            for line in insights_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Limpiar numeración
                    clean_insight = line.replace(line.split('.')[0] + '.', '').strip() if '.' in line else line
                    clean_insight = clean_insight.replace('-', '').replace('•', '').strip()
                    if clean_insight:
                        insights.append(clean_insight)
            
            return insights[:5]  # Máximo 5 insights
            
        except Exception as e:
            self.log(f"❌ Error extrayendo insights: {e}")
            return ["Error extrayendo insights del análisis"]
    
    def _synthesize_curated_content(self, curated_content: Dict[str, Any], 
                                   original_query: str) -> List[str]:
        """Sintetiza todo el contenido curado en notas de síntesis"""
        
        # Preparar resumen de todo el contenido curado
        content_summary = ""
        all_insights = []
        
        for item_key, content in curated_content.items():
            content_summary += f"\n**{content['title']}**:\n"
            content_summary += f"Análisis: {content['analysis'][:200]}...\n"
            all_insights.extend(content['key_insights'])
        
        synthesis_prompt = f"""
        Sintetiza el siguiente contenido curado en notas de síntesis para la consulta original:
        
        CONSULTA ORIGINAL: {original_query}
        
        CONTENIDO CURADO:
        {content_summary}
        
        TODOS LOS INSIGHTS IDENTIFICADOS:
        {chr(10).join(f"- {insight}" for insight in all_insights)}
        
        Crea 5-7 notas de síntesis que:
        1. Conecten los elementos analizados
        2. Identifiquen patrones transversales
        3. Destaquen contradicciones o brechas
        4. Sugieran áreas para profundizar
        5. Proporcionen una perspectiva holística
        
        Responde solo con una lista numerada de notas de síntesis.
        """
        
        try:
            synthesis_text = self.openai_client.generate_response(
                synthesis_prompt,
                task_type="curation",
                max_tokens=500
            )
            
            # Parsear notas de síntesis
            synthesis_notes = []
            for line in synthesis_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    clean_note = line.replace(line.split('.')[0] + '.', '').strip() if '.' in line else line
                    clean_note = clean_note.replace('-', '').replace('•', '').strip()
                    if clean_note:
                        synthesis_notes.append(clean_note)
            
            return synthesis_notes[:7]  # Máximo 7 notas
            
        except Exception as e:
            self.log(f"❌ Error en síntesis: {e}")
            return ["Error generando síntesis del contenido curado"]