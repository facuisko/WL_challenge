"""
Agente reportero que genera reportes finales estructurados
"""
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.tools.openai_client import OpenAIClient
from datetime import datetime
from typing import Dict, Any

class ReporterAgent(BaseAgent):
    """Agente reportero que genera reportes finales profesionales"""
    
    def __init__(self):
        super().__init__("Reportero")
        self._openai_client = None
    
    @property
    def openai_client(self):
        """Lazy loading del cliente OpenAI"""
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client
    
    def execute(self, state: AgenticResearchState) -> AgenticResearchState:
        """Ejecuta generación del reporte final"""
        action = state.get('next_action')
        
        if action == "GENERATE_REPORT":
            return self.generate_final_report(state)
        else:
            return state
    
    def generate_final_report(self, state: AgenticResearchState) -> AgenticResearchState:
        """
        Genera un reporte final estructurado basado en todo el contenido curado
        """
        research_results = state.get('research_results', {})
        research_context = state.get('research_context', {})
        user_query = state['user_query']
        
        if not research_results:
            self.log("❌ No hay contenido curado para generar reporte")
            return {
                **state,
                "current_agent": self.name,
                "final_report": "Error: No hay contenido para generar reporte"
            }
        
        self.log("📄 Generando reporte final estructurado")
        
        # Preparar datos para el reporte
        report_data = self._prepare_report_data(research_results, research_context, user_query)
        
        # Generar cada sección del reporte
        sections = self._generate_report_sections(report_data)
        
        # Ensamblar reporte final
        final_report = self._assemble_final_report(sections, report_data)
        
        # Generar resumen ejecutivo
        executive_summary = self._generate_executive_summary(final_report, user_query)
        
        # Reporte completo con resumen ejecutivo
        complete_report = self._create_complete_report(executive_summary, final_report, report_data)
        
        self.log("✅ Reporte final generado exitosamente")
        
        return {
            **state,
            "current_agent": self.name,
            "final_report": complete_report,
            "strategic_context": {
                "report_generated_at": datetime.now().isoformat(),
                "sections_count": len(sections),
                "total_words": len(complete_report.split()),
                "quality_score": self._assess_report_quality(complete_report)
            }
        }
    
    def _prepare_report_data(self, research_results: Dict[str, Any], 
                           research_context: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Prepara y organiza los datos para el reporte"""
        
        # Extraer todos los análisis
        all_analyses = []
        all_insights = []
        all_sources = []
        
        for item_key, content in research_results.items():
            if isinstance(content, dict):
                all_analyses.append({
                    "title": content.get("title", "Sin título"),
                    "analysis": content.get("analysis", ""),
                    "insights": content.get("key_insights", [])
                })
                all_insights.extend(content.get("key_insights", []))
                
                # Extraer fuentes
                sources = content.get("sources", {})
                if "wikipedia" in sources:
                    all_sources.extend(sources["wikipedia"])
                if "web" in sources:
                    all_sources.extend(sources["web"])
        
        return {
            "query": user_query,
            "analyses": all_analyses,
            "all_insights": all_insights,
            "sources": all_sources,
            "synthesis_notes": research_context.get("synthesis_notes", []),
            "total_items": research_context.get("total_items", 0),
            "completed_items": research_context.get("completed_items", 0)
        }
    
    def _generate_report_sections(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Genera cada sección del reporte usando AI"""
        
        sections = {}
        
        # 1. Introducción y Contexto
        sections["introduction"] = self._generate_introduction(report_data)
        
        # 2. Hallazgos Principales
        sections["main_findings"] = self._generate_main_findings(report_data)
        
        # 3. Análisis Detallado
        sections["detailed_analysis"] = self._generate_detailed_analysis(report_data)
        
        # 4. Insights y Tendencias
        sections["insights_trends"] = self._generate_insights_trends(report_data)
        
        # 5. Conclusiones
        sections["conclusions"] = self._generate_conclusions(report_data)
        
        # 6. Recomendaciones
        sections["recommendations"] = self._generate_recommendations(report_data)
        
        return sections
    
    def _generate_introduction(self, report_data: Dict[str, Any]) -> str:
        """Genera la introducción del reporte"""
        prompt = f"""
        Escribe una introducción profesional para un reporte de investigación sobre:
        
        TEMA: {report_data['query']}
        
        La introducción debe:
        - Establecer el contexto y propósito de la investigación
        - Mencionar que se analizaron {report_data['total_items']} aspectos principales
        - Explicar brevemente la metodología (investigación multi-fuente)
        - Ser concisa pero informativa (150-200 palabras)
        
        Escribe en tono profesional y académico.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=300)
    
    def _generate_main_findings(self, report_data: Dict[str, Any]) -> str:
        """Genera la sección de hallazgos principales"""
        
        insights_text = "\n".join(f"- {insight}" for insight in report_data['all_insights'][:10])
        
        prompt = f"""
        Basado en los siguientes insights de investigación, crea una sección de "Hallazgos Principales":
        
        TEMA: {report_data['query']}
        
        INSIGHTS IDENTIFICADOS:
        {insights_text}
        
        SÍNTESIS:
        {chr(10).join(f"- {note}" for note in report_data['synthesis_notes'])}
        
        Organiza los hallazgos en 4-6 puntos principales que:
        - Destaquen los descubrimientos más importantes
        - Estén respaldados por evidencia
        - Sean relevantes para el tema principal
        - Estén ordenados por importancia
        
        Usa formato markdown con subsecciones.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=600)
    
    def _generate_detailed_analysis(self, report_data: Dict[str, Any]) -> str:
        """Genera la sección de análisis detallado"""
        
        analyses_summary = ""
        for i, analysis in enumerate(report_data['analyses'], 1):
            analyses_summary += f"\n**{i}. {analysis['title']}**\n"
            analyses_summary += f"{analysis['analysis'][:300]}...\n"
        
        prompt = f"""
        Crea una sección de "Análisis Detallado" que sintetice los siguientes análisis:
        
        TEMA: {report_data['query']}
        
        ANÁLISIS REALIZADOS:
        {analyses_summary}
        
        Esta sección debe:
        - Profundizar en los aspectos técnicos y conceptuales
        - Conectar los diferentes análisis realizados
        - Identificar patrones y relaciones entre elementos
        - Proporcionar contexto y explicaciones detalladas
        - Mantener estructura clara con subsecciones
        
        Usa formato markdown y mantén tono analítico.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=800)
    
    def _generate_insights_trends(self, report_data: Dict[str, Any]) -> str:
        """Genera la sección de insights y tendencias"""
        
        prompt = f"""
        Basado en la investigación sobre "{report_data['query']}", crea una sección de "Insights y Tendencias":
        
        INSIGHTS CLAVE:
        {chr(10).join(f"- {insight}" for insight in report_data['all_insights'])}
        
        NOTAS DE SÍNTESIS:
        {chr(10).join(f"- {note}" for note in report_data['synthesis_notes'])}
        
        Esta sección debe incluir:
        - Tendencias emergentes identificadas
        - Patrones significativos
        - Implicaciones futuras
        - Oportunidades y desafíos
        - Perspectivas de evolución
        
        Estructura con subsecciones claras en markdown.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=600)
    
    def _generate_conclusions(self, report_data: Dict[str, Any]) -> str:
        """Genera las conclusiones del reporte"""
        
        prompt = f"""
        Escribe conclusiones sólidas para el reporte de investigación sobre:
        
        TEMA: {report_data['query']}
        
        Las conclusiones deben:
        - Sintetizar los hallazgos más importantes
        - Responder a las preguntas clave sobre el tema
        - Proporcionar una perspectiva general informada
        - Mencionar limitaciones de la investigación
        - Ser concisas pero comprehensivas
        
        Longitud: 200-300 palabras.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=400)
    
    def _generate_recommendations(self, report_data: Dict[str, Any]) -> str:
        """Genera recomendaciones basadas en la investigación"""
        
        prompt = f"""
        Basado en la investigación sobre "{report_data['query']}", proporciona recomendaciones prácticas:
        
        Las recomendaciones deben:
        - Ser específicas y accionables
        - Estar basadas en los hallazgos de la investigación
        - Dirigirse a diferentes audiencias (si aplica)
        - Incluir próximos pasos sugeridos
        - Ser realistas e implementables
        
        Organiza en 3-5 recomendaciones principales con formato markdown.
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=500)
    
    def _generate_executive_summary(self, full_report: str, query: str) -> str:
        """Genera un resumen ejecutivo del reporte completo"""
        
        prompt = f"""
        Crea un resumen ejecutivo conciso para este reporte de investigación:
        
        TEMA: {query}
        
        REPORTE COMPLETO:
        {full_report[:2000]}...
        
        El resumen ejecutivo debe:
        - Capturar los puntos más importantes en 100-150 palabras
        - Ser autocontenido y legible independientemente
        - Destacar hallazgos clave y conclusiones principales
        - Usar lenguaje claro y directo
        """
        
        return self.openai_client.generate_response(prompt, task_type="report", max_tokens=250)
    
    def _assemble_final_report(self, sections: Dict[str, str], report_data: Dict[str, Any]) -> str:
        """Ensambla todas las secciones en un reporte final"""
        
        report = f"""# Reporte de Investigación: {report_data['query']}

## Introducción
{sections['introduction']}

## Hallazgos Principales
{sections['main_findings']}

## Análisis Detallado
{sections['detailed_analysis']}

## Insights y Tendencias
{sections['insights_trends']}

## Conclusiones
{sections['conclusions']}

## Recomendaciones
{sections['recommendations']}

---

### Metodología
Esta investigación se basó en análisis multi-fuente incluyendo {len(report_data['sources'])} fuentes académicas y web, con síntesis automatizada de {report_data['total_items']} aspectos principales del tema.

### Fuentes Consultadas
{self._format_sources(report_data['sources'])}
"""
        
        return report
    
    def _create_complete_report(self, executive_summary: str, full_report: str, 
                              report_data: Dict[str, Any]) -> str:
        """Crea el reporte completo con resumen ejecutivo"""
        
        complete_report = f"""# 📊 REPORTE DE INVESTIGACIÓN COMPLETO

**Tema:** {report_data['query']}  
**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  
**Análisis completados:** {report_data['completed_items']}/{report_data['total_items']}

---

## 🎯 Resumen Ejecutivo

{executive_summary}

---

{full_report}

---

## 📈 Métricas del Reporte
- **Fuentes analizadas:** {len(report_data['sources'])}
- **Insights extraídos:** {len(report_data['all_insights'])}
- **Notas de síntesis:** {len(report_data['synthesis_notes'])}
- **Palabras totales:** ~{len(full_report.split())} palabras

*Reporte generado por el Sistema de Agentes de Investigación*
"""
        
        return complete_report
    
    def _format_sources(self, sources: list) -> str:
        """Formatea la lista de fuentes"""
        if not sources:
            return "No se encontraron fuentes específicas."
        
        formatted = []
        for i, source in enumerate(sources[:10], 1):  # Máximo 10 fuentes
            if isinstance(source, dict):
                title = source.get('title', 'Sin título')
                source_type = source.get('source', 'Desconocido')
                formatted.append(f"{i}. **{title}** - {source_type}")
        
        return "\n".join(formatted) if formatted else "Fuentes procesadas automáticamente."
    
    def _assess_report_quality(self, report: str) -> float:
        """Evalúa la calidad del reporte generado"""
        
        # Métricas básicas de calidad
        word_count = len(report.split())
        section_count = report.count('##')
        has_sources = 'Fuentes' in report
        has_conclusions = 'Conclusiones' in report
        has_recommendations = 'Recomendaciones' in report
        
        # Cálculo de puntuación (0-1)
        quality_score = 0.0
        
        # Longitud apropiada (0.3 puntos)
        if 800 <= word_count <= 2000:
            quality_score += 0.3
        elif 500 <= word_count <= 2500:
            quality_score += 0.2
        
        # Estructura completa (0.4 puntos)
        if section_count >= 5:
            quality_score += 0.2
        if has_sources:
            quality_score += 0.1
        if has_conclusions:
            quality_score += 0.05
        if has_recommendations:
            quality_score += 0.05
        
        # Contenido coherente (0.3 puntos)
        if 'Hallazgos' in report:
            quality_score += 0.1
        if 'Análisis' in report:
            quality_score += 0.1
        if 'Resumen Ejecutivo' in report:
            quality_score += 0.1
        
        return min(quality_score, 1.0)  # Máximo 1.0