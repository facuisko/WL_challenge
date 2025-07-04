"""
Agente curador que realiza análisis profundo del contenido aprobado
"""
from typing import Dict, Any, List
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.tools.openai_client import OpenAIClient
import re

class CuratorAgent(BaseAgent):
    """Agente curador que sintetiza y analiza información aprobada"""
    
    def __init__(self):
        super().__init__("Curador")
        self._openai_client = None
    
    @property
    def openai_client(self):
        """Lazy loading del cliente OpenAI"""
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client
    
    def execute(self, state: AgenticResearchState) -> AgenticResearchState:
        """Ejecuta la curación de contenido"""
        action = state.get('next_action')
        
        self.log(f"🔧 Curador ejecutando acción: {action}")
        
        if action == "CURATE_CONTENT":
            return self.curate_approved_content(state)
        else:
            self.log(f"⚠️ Acción no reconocida: {action}")
            return state
    
    def curate_approved_content(self, state: AgenticResearchState) -> AgenticResearchState:
        """
        Realiza análisis profundo del contenido aprobado por el usuario
        Cumple con: 'Takes approved findings and performs deeper analysis'
        """
        user_query = state['user_query']
        outline_items = state.get('outline_items', [])
        
        self.log(f"🔍 Iniciando curación profunda para: '{user_query}'")
        self.log(f"📋 Procesando {len(outline_items)} secciones aprobadas")
        
        # Si no hay outline_items, extraer del proposed_outline
        if not outline_items and state.get('proposed_outline'):
            outline_items = self._extract_titles_from_outline(state['proposed_outline'])
            self.log(f"🔧 Extrayendo títulos del esquema propuesto: {len(outline_items)} títulos")
        
        # Realizar análisis profundo de cada elemento aprobado
        curated_sections = []
        total_sections = len(outline_items)
        
        for i, section_title in enumerate(outline_items, 1):
            progress = int((i / total_sections) * 100)  # Progreso del 0% al 100%
            progress_bar = "█" * (progress // 4) + "░" * (25 - progress // 4)  # Barra de 25 caracteres
            print(f"\r🔎 Curando contenido: [{progress_bar}] {progress}% - Sección {i}/{total_sections}", end="", flush=True)
            
            self.log(f"\n   🔍 Curando sección {i}: {section_title[:50]}...")
            
            # Realizar análisis profundo de la sección
            curated_content = self._analyze_section_deeply(section_title, user_query)
            
            curated_sections.append({
                "title": section_title,
                "content": curated_content,
                "section_number": i
            })
        
        print()  # Nueva línea después del progreso
        
        # Sintetizar información de múltiples perspectivas
        synthesis = self._synthesize_multi_perspective_analysis(curated_sections, user_query)
        
        # Preparar análisis estructurado para el reportero
        analysis_complete = {
            "curated_sections": curated_sections,
            "multi_perspective_synthesis": synthesis,
            "research_depth": "comprehensive_analysis",
            "total_sections": len(curated_sections),
            "analysis_method": "deep_content_curation"
        }
        
        self.log("✅ Curación de contenido completada")
        
        return {
            **state,
            "current_agent": self.name,
            "analysis_complete": analysis_complete,
            "curated_content": curated_sections,
            "research_synthesis": synthesis
        }
    
    def _extract_titles_from_outline(self, outline: str) -> List[str]:
        """Extrae títulos del esquema propuesto"""
        lines = outline.split('\n')
        titles = []
        for line in lines:
            line = line.strip()
            if line.startswith('###') or line.startswith('##') or (line.startswith('-') and len(line) > 5):
                # Limpiar marcadores markdown
                clean_title = re.sub(r'^#{1,4}\s*', '', line)
                clean_title = re.sub(r'^-\s*', '', clean_title)
                # Eliminar numeración inicial (ej: "1. ", "2. ", etc.)
                clean_title = re.sub(r'^\d+\.\s*', '', clean_title)
                # Excluir líneas que contengan "ESQUEMA DE INVESTIGACIÓN"
                if clean_title and "ESQUEMA DE INVESTIGACIÓN" not in clean_title.upper():
                    titles.append(clean_title)
        # Limitar a máximo 6 elementos
        return titles[:6]
    
    def _analyze_section_deeply(self, section_title: str, main_query: str) -> str:
        """
        Realiza análisis profundo de una sección específica
        Usa modelos más potentes para análisis complejo
        """
        analysis_prompt = f"""
        Realiza un análisis profundo y detallado sobre: "{section_title}"
        
        CONTEXTO PRINCIPAL: {main_query}
        
        INSTRUCCIONES PARA ANÁLISIS PROFUNDO:
        1. Desarrolla el tema con profundidad académica y rigor
        2. Integra información de múltiples perspectivas
        3. Incluye datos específicos, tendencias y desarrollos recientes
        4. Identifica implicaciones y conexiones importantes
        5. Proporciona ejemplos concretos cuando sea relevante
        6. Mantén un enfoque analítico y estructurado
        7. Usa conocimiento actualizado y relevante
        
        FORMATO DE RESPUESTA:
        - Introducción conceptual del tema
        - Desarrollo analítico detallado (3-4 párrafos)
        - Datos y evidencia específica
        - Tendencias actuales y desarrollos recientes
        - Implicaciones y análisis crítico
        - Ejemplos prácticos o casos de estudio relevantes
        
        Genera un análisis de 400-500 palabras que sea informativo, bien estructurado y académicamente riguroso.
        """
        
        try:
            # Usar modelo potente para análisis complejo (task_type="analysis")
            analysis = self.openai_client.generate_response(
                analysis_prompt, 
                task_type="analysis",  # Usará modelo más potente
                max_tokens=600
            )
            return analysis
            
        except Exception as e:
            self.log(f"❌ Error en análisis profundo de '{section_title}': {e}")
            return f"**{section_title}**\n\nAnálisis en desarrollo. Se requiere investigación adicional sobre este aspecto de {main_query}."
    
    def _synthesize_multi_perspective_analysis(self, curated_sections: List[Dict], main_query: str) -> str:
        """
        Sintetiza información desde múltiples perspectivas para crear una visión integral
        Cumple con: 'Synthesizes information from multiple sources'
        """
        sections_overview = "\n".join([
            f"{i}. {section['title']}" 
            for i, section in enumerate(curated_sections, 1)
        ])
        
        synthesis_prompt = f"""
        Crea una síntesis integral que conecte múltiples perspectivas y análisis sobre: "{main_query}"
        
        SECCIONES ANALIZADAS:
        {sections_overview}
        
        OBJETIVO DE SÍNTESIS:
        1. Identifica patrones y temas transversales entre las secciones
        2. Conecta ideas y conceptos de diferentes perspectivas
        3. Destaca hallazgos más significativos del análisis
        4. Identifica áreas de convergencia y complementariedad
        5. Proporciona una visión holística e integrada del tema
        6. Resalta tendencias emergentes y direcciones futuras
        
        FORMATO DE RESPUESTA:
        ## Síntesis Multi-Perspectiva
        
        ### Hallazgos Principales
        [3-4 hallazgos clave que emergen del análisis integral]
        
        ### Conexiones Transversales
        [Cómo se relacionan e integran las diferentes perspectivas]
        
        ### Tendencias Emergentes
        [Patrones y direcciones futuras identificadas]
        
        ### Consideraciones Críticas
        [Aspectos importantes y áreas que requieren atención]
        
        ### Visión Integral
        [Perspectiva unificada que integra todos los análisis]
        
        Genera una síntesis de 300-350 palabras que integre múltiples perspectivas de manera coherente y significativa.
        """
        
        try:
            # Usar modelo potente para síntesis compleja
            synthesis = self.openai_client.generate_response(
                synthesis_prompt, 
                task_type="synthesis",  # Usará modelo más potente
                max_tokens=450
            )
            return synthesis
            
        except Exception as e:
            self.log(f"❌ Error en síntesis multi-perspectiva: {e}")
            return "## Síntesis Multi-Perspectiva\n\n[Error en generación de síntesis integral]\n\nSe requiere análisis adicional para completar la síntesis."