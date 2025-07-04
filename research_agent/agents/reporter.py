"""
Agente reportero que genera reportes finales estructurados
"""
from typing import Dict, Any, List
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.tools.openai_client import OpenAIClient
import datetime
import os
import re

class ReporterAgent(BaseAgent):
    """Agente reportero que transforma contenido curado en reportes pulidos"""
    
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
        """Ejecuta la generación de reporte"""
        action = state.get('next_action')
        
        if action == "GENERATE_REPORT":
            return self.generate_final_report(state)
        else:
            return state
    
    def generate_final_report(self, state: AgenticResearchState) -> AgenticResearchState:
        """
        Genera reporte final pulido siguiendo exactamente el índice aprobado por el usuario
        Cumple con: 'Transforms analyzed content into a polished final report'
        """
        user_query = state['user_query']
        outline_items = state.get('outline_items', [])  # Esquema aprobado por usuario
        analysis_complete = state.get('analysis_complete', {})
        curated_content = analysis_complete.get('curated_sections', [])
        synthesis = state.get('research_synthesis', '')
        
        self.log(f"📄 Generando reporte final para: '{user_query}'")
        self.log(f"📋 Siguiendo esquema aprobado con {len(outline_items)} secciones")
        self.log(f"📚 Contenido curado disponible: {len(curated_content)} secciones")
        
        # Iniciar progreso del reporte
        total_steps = 5
        
        # Paso 1: Generar reporte estructurado siguiendo índice aprobado
        self._show_progress(1, total_steps, "Generando reporte estructurado...")
        final_report = self._create_structured_report_from_approved_outline(
            user_query, 
            outline_items,  # Esquema aprobado por usuario
            curated_content, 
            synthesis
        )
        
        # Paso 2: Generar resumen ejecutivo
        self._show_progress(2, total_steps, "Creando resumen ejecutivo...")
        executive_summary = self._create_executive_summary(
            user_query, 
            curated_content, 
            synthesis
        )
        
        # Paso 3: Información sobre el análisis realizado
        self._show_progress(3, total_steps, "Compilando información del análisis...")
        analysis_info = self._create_analysis_info_section(analysis_complete)
        
        # Paso 4: Compilar reporte completo
        self._show_progress(4, total_steps, "Compilando reporte completo...")
        complete_report = self._compile_complete_report(
            user_query,
            executive_summary,
            final_report,
            analysis_info,
            analysis_complete
        )
        
        # Paso 5: Guardar reporte en archivo markdown
        self._show_progress(5, total_steps, "Guardando archivo markdown...")
        file_path = self._save_report_to_file(complete_report, user_query)
        
        # Progreso completo
        self._show_progress(5, total_steps, "¡Reporte completado!", complete=True)
        
        self.log("✅ Reporte final generado exitosamente")
        if file_path:
            self.log(f"📁 Reporte guardado en: {file_path}")
        
        return {
            **state,
            "current_agent": self.name,
            "final_report": complete_report,
            "executive_summary": executive_summary,
            "report_file_path": file_path,
            "report_metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "sections_count": len(curated_content),
                "word_count": len(complete_report.split()),
                "analysis_depth": analysis_complete.get('research_depth', 'comprehensive'),
                "file_path": file_path
            }
        }
    
    def _create_structured_report_from_approved_outline(self, query: str, outline_items: List[str], 
                                                       curated_sections: List[Dict], synthesis: str) -> str:
        """
        Crea el reporte siguiendo exactamente el índice/esquema aprobado por el usuario
        """
        self.log(f"📋 Estructurando reporte según esquema aprobado: {len(outline_items)} secciones")
        
        # Mapear contenido curado con los elementos del esquema aprobado
        structured_content = ""
        
        for i, approved_title in enumerate(outline_items, 1):
            # Buscar el contenido curado correspondiente a este título
            matching_content = self._find_content_for_approved_title(approved_title, curated_sections)
            
            # Agregar sección al reporte
            structured_content += f"\n\n## {i}. {approved_title}\n\n"
            
            if matching_content:
                # Usar el contenido curado disponible
                structured_content += matching_content
                self.log(f"   ✅ Sección {i}: Contenido encontrado y mapeado")
            else:
                # Generar contenido básico si no hay match
                basic_content = self._generate_basic_content_for_title(approved_title, query)
                structured_content += basic_content
                self.log(f"   ⚠️ Sección {i}: Generando contenido básico")
        
        # Crear reporte completo usando el formato del usuario
        sections_list = "\n".join([f"{i}. {title}" for i, title in enumerate(outline_items, 1)])
        
        report_prompt = f"""
        Crea un reporte de investigación profesional siguiendo EXACTAMENTE esta estructura aprobada por el usuario:

        ESQUEMA APROBADO:
        {sections_list}
        
        CONTENIDO DISPONIBLE POR SECCIÓN:
        {structured_content}
        
        SÍNTESIS PARA INTEGRAR:
        {synthesis}
        
        INSTRUCCIONES CRÍTICAS:
        1. RESPETA EXACTAMENTE el orden y títulos del esquema aprobado
        2. Usa los títulos EXACTOS como aparecen en el esquema
        3. NO reorganices ni cambies la estructura aprobada
        4. INCLUYE TODAS LAS 6 SECCIONES COMPLETAS Y DESARROLLADAS
        5. Integra el contenido disponible en cada sección correspondiente
        6. Mantén un tono académico pero accesible
        7. Asegúrate de que cada sección tenga contenido sustancial (300-400 palabras mínimo)
        8. INCLUYE el índice aprobado al inicio del reporte
        9. COMPLETA TODAS LAS SECCIONES - NO CORTES EL CONTENIDO
        
        FORMATO DE RESPUESTA (Markdown):
        # {query}
        
        ## 📋 Índice General
        
        ### Estructura del Reporte
        1. **Introducción** - Presentación del tema y metodología
        2. **Contenido Principal** - Análisis detallado por secciones:
        {chr(10).join([f"   - {i}. {title}" for i, title in enumerate(outline_items, 1)])}
        3. **Conclusiones** - Síntesis final y hallazgos clave
        
        ### Secciones Complementarias
        - **Resumen Ejecutivo** - Síntesis para toma de decisiones
        - **Información del Análisis** - Metodología y proceso
        - **Arquitectura del Sistema** - Tecnología utilizada
        
        ---
        
        ## Introducción
        [Breve introducción al tema y estructura del reporte - explicando que se analizarán las {len(outline_items)} secciones del índice principal]
        
        {chr(10).join([f"## {i}. {title}" + chr(10) + "[Desarrollar COMPLETAMENTE esta sección con mínimo 300 palabras sustanciales]" + chr(10) for i, title in enumerate(outline_items, 1)])}
        
        ## Conclusiones
        [Síntesis final integrando todos los aspectos del esquema aprobado]
        
        IMPORTANTE: 
        - Mantén EXACTAMENTE los títulos y numeración del esquema aprobado
        - DESARROLLA COMPLETAMENTE todas las 6 secciones SIN EXCEPCIÓN
        - NO cortes el contenido a la mitad - termina cada sección completamente
        - Incluye el índice completo al inicio
        - Asegúrate de que el reporte tenga todas las secciones numeradas del 1 al 6
        """
        
        try:
            # Usar modelo de alta calidad para reporte final
            report = self.openai_client.generate_response(
                report_prompt, 
                task_type="final_report",  # Máxima calidad
                max_tokens=3000  # Aumentado para permitir reportes completos
            )
            
            self.log("✅ Reporte estructurado según esquema aprobado")
            return report
            
        except Exception as e:
            self.log(f"❌ Error generando reporte estructurado: {e}")
            return self._generate_fallback_structured_report(query, outline_items, curated_sections)
    
    def _find_content_for_approved_title(self, approved_title: str, curated_sections: List[Dict]) -> str:
        """Busca el contenido curado que corresponde a un título aprobado"""
        # Buscar coincidencia exacta primero
        for section in curated_sections:
            if section['title'].strip() == approved_title.strip():
                return section['content']
        
        # Buscar coincidencia parcial
        approved_lower = approved_title.lower()
        for section in curated_sections:
            section_lower = section['title'].lower()
            if approved_lower in section_lower or section_lower in approved_lower:
                return section['content']
        
        return None
    
    def _generate_basic_content_for_title(self, title: str, main_query: str) -> str:
        """Genera contenido básico para un título cuando no hay contenido curado disponible"""
        try:
            basic_prompt = f"""
            Genera un análisis básico sobre: "{title}"
            
            CONTEXTO: Este es parte de una investigación sobre "{main_query}"
            
            INSTRUCCIONES:
            1. Proporciona información relevante y precisa sobre el tema
            2. Mantén un enfoque académico
            3. Incluye 2-3 párrafos de desarrollo
            4. Conecta con el tema principal de investigación
            5. Evita especulaciones, usa información verificable
            
            Genera contenido de 200-300 palabras.
            """
            
            content = self.openai_client.generate_response(
                basic_prompt,
                task_type="content_generation",
                max_tokens=400
            )
            return content
            
        except Exception as e:
            return f"**{title}**\n\nContenido no disponible para esta sección. Se requiere análisis adicional sobre este aspecto de {main_query}."
    
    def _generate_fallback_structured_report(self, query: str, outline_items: List[str], curated_sections: List[Dict]) -> str:
        """Genera reporte de respaldo cuando falla la generación principal"""
        report = f"# {query}\n\n"
        report += "## Introducción\n\nEste reporte presenta un análisis del tema solicitado.\n\n"
        
        for i, title in enumerate(outline_items, 1):
            report += f"## {i}. {title}\n\n"
            
            # Buscar contenido correspondiente
            matching_content = self._find_content_for_approved_title(title, curated_sections)
            if matching_content:
                report += matching_content + "\n\n"
            else:
                report += f"Análisis pendiente para: {title}\n\n"
        
        report += "## Conclusiones\n\nSe requiere análisis adicional para completar la investigación.\n\n"
        return report
    
    def _create_structured_report(self, query: str, curated_sections: List[Dict], 
                                synthesis: str, research_context: Dict) -> str:
        """
        Crea el cuerpo principal del reporte estructurado
        Usa modelo de alta calidad para output pulido
        """
        sections_content = "\n\n".join([
            f"SECCIÓN {section['section_number']}: {section['title']}\n{section['content']}"
            for section in curated_sections
        ])
        
        sources_count = len(research_context.get('source_summaries', []))
        
        report_prompt = f"""
        Crea un reporte de investigación profesional y bien estructurado sobre: "{query}"
        
        CONTENIDO CURADO DISPONIBLE:
        {sections_content}
        
        SÍNTESIS MULTI-FUENTE:
        {synthesis}
        
        FUENTES CONSULTADAS: {sources_count} fuentes verificadas
        
        INSTRUCCIONES PARA REPORTE FINAL:
        1. Usa un tono académico pero accesible
        2. Estructura el contenido de manera lógica y fluida
        3. Integra las secciones de manera coherente
        4. Incluye transiciones suaves entre temas
        5. Mantén rigor académico y profesionalismo
        6. Evita repeticiones innecesarias
        7. Proporciona conclusiones bien fundamentadas
        
        FORMATO DE RESPUESTA (Markdown):
        # {query}
        
        ## Introducción
        [Contexto y relevancia del tema - 2-3 párrafos]
        
        ## Desarrollo Principal
        [Integración fluida del contenido curado organizando las secciones de manera lógica]
        
        ## Análisis y Tendencias
        [Integración de la síntesis multi-fuente con análisis crítico]
        
        ## Conclusiones
        [Síntesis final con hallazgos principales y perspectivas futuras]
        
        Genera un reporte completo, profesional y bien estructurado que integre todo el contenido de manera coherente.
        """
        
        try:
            # Usar modelo de alta calidad para reporte final (task_type="report")
            report = self.openai_client.generate_response(
                report_prompt, 
                task_type="report",  # Usará el modelo más potente
                max_tokens=1500
            )
            return report
            
        except Exception as e:
            self.log(f"❌ Error generando reporte estructurado: {e}")
            return f"# {query}\n\n[Error en generación de reporte final]"
    
    def _create_executive_summary(self, query: str, curated_sections: List[Dict], 
                                synthesis: str) -> str:
        """
        Crea resumen ejecutivo del reporte
        """
        key_points = []
        for section in curated_sections[:3]:  # Top 3 secciones
            title = section['title']
            content_preview = section['content'][:200] + "..."
            key_points.append(f"• {title}: {content_preview}")
        
        key_points_text = "\n".join(key_points)
        
        summary_prompt = f"""
        Crea un resumen ejecutivo conciso para una investigación sobre: "{query}"
        
        PUNTOS CLAVE IDENTIFICADOS:
        {key_points_text}
        
        SÍNTESIS DISPONIBLE:
        {synthesis[:300]}...
        
        OBJETIVO DEL RESUMEN EJECUTIVO:
        1. Capturar los hallazgos más importantes en 3-4 párrafos
        2. Usar lenguaje claro y directo
        3. Destacar implicaciones prácticas
        4. Proporcionar valor inmediato al lector
        
        FORMATO:
        ## Resumen Ejecutivo
        
        [3-4 párrafos concisos que capturen la esencia de la investigación]
        
        ### Hallazgos Clave
        • [Hallazgo 1]
        • [Hallazgo 2]
        • [Hallazgo 3]
        
        ### Implicaciones Principales
        [1-2 párrafos sobre las implicaciones más importantes]
        
        Genera un resumen ejecutivo de 200-250 palabras.
        """
        
        try:
            summary = self.openai_client.generate_response(
                summary_prompt, 
                task_type="summary",
                max_tokens=350
            )
            return summary
            
        except Exception as e:
            self.log(f"❌ Error generando resumen ejecutivo: {e}")
            return "## Resumen Ejecutivo\n\n[Error en generación de resumen ejecutivo]"
    
    def _create_analysis_info_section(self, analysis_complete: Dict) -> str:
        """
        Crea sección con información del análisis realizado
        """
        total_sections = analysis_complete.get('total_sections', 0)
        research_depth = analysis_complete.get('research_depth', 'básico')
        analysis_method = analysis_complete.get('analysis_method', 'curación de contenido')
        
        analysis_info = f"""## 📊 Información del Análisis

### Especificaciones Técnicas
- **Desarrollador del Sistema**: Facundo Iskowitz
- **Método de análisis**: {analysis_method}
- **Profundidad de investigación**: {research_depth}
- **Secciones analizadas**: {total_sections}
- **Arquitectura**: Multi-agente con LangGraph

### Proceso de Curación Inteligente
Este reporte ha sido generado mediante un proceso de análisis profundo que incluye:
1. **Validación humana** del esquema de investigación
2. **Análisis detallado** de cada sección temática
3. **Síntesis multi-perspectiva** de los hallazgos
4. **Estructuración académica** del contenido
5. **Optimización de costos** mediante selección inteligente de modelos

### Garantía de Calidad
- **Rigor académico**: Estándares científicos aplicados
- **Múltiples perspectivas**: Análisis integral del tema
- **Validación humana**: Supervisión en puntos críticos
- **Trazabilidad**: Proceso documentado y reproducible

### Tecnologías Utilizadas
- **LangGraph**: Orquestación de agentes inteligentes
- **OpenAI GPT**: Modelos de lenguaje optimizados
- **Python**: Lenguaje de programación principal
- **Markdown**: Formato de salida estructurado"""
        
        return analysis_info
    
    def _compile_complete_report(self, query: str, executive_summary: str, 
                               main_report: str, analysis_info: str, 
                               analysis_complete: Dict) -> str:
        """
        Compila el reporte completo con todas las secciones
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sections_count = analysis_complete.get('total_sections', 0)
        
        complete_report = f"""# Reporte de Investigación: {query}

**Autor:** Facundo Iskowitz  
**Fecha de generación:** {timestamp}  
**Secciones analizadas:** {sections_count}  
**Sistema:** Multi-Agente de Investigación Inteligente  

---

{main_report}

---

{executive_summary}

---

{analysis_info}

---

## Metodología del Sistema

Este reporte fue generado mediante un sistema multi-agente desarrollado por **Facundo Iskowitz** que incluye:

### Arquitectura de Agentes
- **🤖 Supervisor:** Coordinación inteligente del flujo de trabajo
- **🔍 Investigador:** Generación y estructuración de esquemas de investigación
- **📚 Curador:** Análisis profundo y síntesis multi-perspectiva
- **📄 Reportero:** Generación de reportes finales estructurados

### Proceso de Investigación
1. **Análisis inicial** del tema de investigación
2. **Generación de esquema** con validación humana
3. **Curación profunda** de contenido por secciones
4. **Síntesis multi-perspectiva** de hallazgos
5. **Generación de reporte** final estructurado

### Características Técnicas
- **Human-in-the-loop validation** para máxima precisión
- **Cost optimization** mediante selección inteligente de modelos
- **Multi-perspective analysis** para visión integral
- **Structured reporting** con formato académico

---

*Reporte generado por el Sistema Multi-Agente de Investigación*  
*Desarrollado por **Facundo Iskowitz***  
*Powered by LangGraph & OpenAI*
"""
        
        return complete_report
    
    def _save_report_to_file(self, report_content: str, user_query: str) -> str:
        """
        Guarda el reporte en un archivo markdown
        Cumple con: 'Generates final report in predefined format (markdown recommended)'
        """
        try:
            # Crear nombre de archivo limpio
            safe_filename = self._create_safe_filename(user_query)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"reporte_{safe_filename}_{timestamp}.md"
            
            # Guardar en directorio actual, crear subdirectorio solo si no existe
            reports_dir = "reportes"
            try:
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                    self.log(f"📁 Directorio '{reports_dir}' creado automáticamente")
                
                # Ruta completa del archivo
                file_path = os.path.join(reports_dir, filename)
            except Exception:
                # Si no puede crear la carpeta, guarda en directorio actual
                self.log("⚠️ No se pudo crear carpeta 'reportes', guardando en directorio actual")
                file_path = filename
            
            # Guardar el reporte
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log(f"💾 Archivo guardado exitosamente: {file_path}")
            return file_path
            
        except Exception as e:
            self.log(f"❌ Error guardando archivo: {e}")
            return None
    
    def _create_safe_filename(self, query: str) -> str:
        """Crea un nombre de archivo seguro a partir del query del usuario"""
        # Limpiar caracteres especiales
        safe_name = re.sub(r'[^\w\s-]', '', query.lower())
        # Reemplazar espacios con guiones bajos
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        # Limitar longitud
        safe_name = safe_name[:50]
        # Remover guiones bajos al inicio/final
        safe_name = safe_name.strip('_')
        
        return safe_name if safe_name else "investigacion"
    
    def _show_progress(self, current: int, total: int, message: str, complete: bool = False):
        """Muestra barra de progreso en tiempo real"""
        if complete:
            percentage = 100
            progress_bar = "█" * 30
        else:
            percentage = int((current / total) * 100)
            filled = int((current / total) * 30)
            progress_bar = "█" * filled + "░" * (30 - filled)
        
        status_icon = "✅" if complete else "📊"
        print(f"\r{status_icon} Generando reporte: [{progress_bar}] {percentage}% - {message}", end="", flush=True)
        
        if complete:
            print()  # Nueva línea al completar