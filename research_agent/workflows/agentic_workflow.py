"""
Workflow agéntico completo con todos los agentes
"""
from langgraph.graph import StateGraph, END
from research_agent.models.agentic_state import AgenticResearchState
from research_agent.agents.supervisor import SupervisorAgent
from research_agent.agents.investigator import InvestigatorAgent
from research_agent.agents.curator import CuratorAgent
from research_agent.agents.reporter import ReporterAgent

class AgenticResearchWorkflow:
    """Workflow completo de investigación con múltiples agentes"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.investigator = InvestigatorAgent()
        self.curator = CuratorAgent()
        self.reporter = ReporterAgent()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Crea el grafo completo de LangGraph"""
        workflow = StateGraph(AgenticResearchState)
        
        # Agregar todos los agentes como nodos
        workflow.add_node("supervisor", self.supervisor.execute)
        workflow.add_node("investigator", self.investigator.execute)
        workflow.add_node("curator", self.curator.execute)
        workflow.add_node("reporter", self.reporter.execute)
        
        # Punto de entrada siempre es el supervisor
        workflow.set_entry_point("supervisor")
        
        # Edges condicionales desde supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "investigator": "investigator",
                "curator": "curator",
                "reporter": "reporter",
                "continue": "supervisor",  # Loop back para validación humana
                "end": END
            }
        )
        
        # Todos los agentes regresan al supervisor para coordinación
        workflow.add_edge("investigator", "supervisor")
        workflow.add_edge("curator", "supervisor")
        workflow.add_edge("reporter", "supervisor")
        
        return workflow.compile()
    
    def _route_from_supervisor(self, state: AgenticResearchState) -> str:
        """Enruta desde el supervisor a los agentes apropiados"""
        action = state.get('next_action')
        
        # Mapeo directo de acciones a agentes
        action_routing = {
            "GENERATE_OUTLINE": "investigator",
            "CURATE_CONTENT": "curator", 
            "GENERATE_REPORT": "reporter",
            "FINISH": "end"
        }
        
        if action in action_routing:
            return action_routing[action]
        
        # Si no hay acción específica, continuar con el supervisor
        # (esto sucede durante la validación humana)
        return "continue"
    
    def run(self, user_query: str = None) -> AgenticResearchState:
        """
        Ejecuta el workflow completo de investigación
        
        Args:
            user_query: Tema de investigación (opcional, se puede preguntar interactivamente)
            
        Returns:
            Estado final con el reporte completo
        """
        print("🚀 SISTEMA DE INVESTIGACIÓN AGÉNTICO INICIADO")
        print("=" * 60)
        
        # Estado inicial
        initial_state = {
            "user_query": user_query,
            "proposed_outline": "",
            "outline_approved": False,
            "outline_items": [],
            "user_feedback": "",
            
            # Estado agéntico avanzado
            "current_research_topic": user_query or "",
            "research_context": {},
            "agent_decisions": {},
            "autonomous_actions": [],
            "quality_assessments": {},
            "inter_agent_messages": [],
            
            # Control de flujo
            "current_agent": "",
            "next_action": "",
            "supervisor_reasoning": "",
            "strategic_context": {},
            
            # Resultados
            "research_results": {},
            "analysis_complete": False,
            "final_report": "",
            
            # Metadatos
            "step_count": 0,
            "conversation_history": []
        }
        
        try:
            # Ejecutar workflow
            print("\n🔄 Iniciando workflow de investigación...")
            result = self.workflow.invoke(initial_state)
            
            # Mostrar resultados finales
            self._display_comprehensive_results(result)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error en el workflow: {e}")
            print("🔧 Revisa la configuración y dependencias")
            
            # Retornar estado de error
            return {
                **initial_state,
                "final_report": f"Error en el proceso: {str(e)}",
                "current_agent": "Sistema",
                "step_count": 1
            }
    
    def _display_comprehensive_results(self, result: AgenticResearchState):
        """Muestra los resultados finales del proceso completo"""
        print("\n" + "="*80)
        print("🎉 PROCESO DE INVESTIGACIÓN COMPLETADO")
        print("="*80)
        
        # Información general
        print(f"\n📋 Tema investigado: {result.get('user_query', 'No especificado')}")
        print(f"⏱️  Pasos ejecutados: {result.get('step_count', 0)}")
        print(f"🤖 Último agente: {result.get('current_agent', 'Desconocido')}")
        
        # Calidad del proceso
        strategic_context = result.get('strategic_context', {})
        if strategic_context:
            print(f"\n📊 MÉTRICAS DE CALIDAD:")
            print(f"   • Secciones del reporte: {strategic_context.get('sections_count', 0)}")
            print(f"   • Palabras totales: {strategic_context.get('total_words', 0)}")
            quality_score = strategic_context.get('quality_score', 0)
            print(f"   • Puntuación de calidad: {quality_score:.2f}/1.00")
        
        # Decisiones de agentes
        agent_decisions = result.get('agent_decisions', {})
        if agent_decisions:
            print(f"\n🧠 DECISIONES DE AGENTES:")
            for step, decision in agent_decisions.items():
                agent = decision.get('agent', 'Unknown')
                reasoning = decision.get('reasoning', 'No reasoning')
                print(f"   • {step}: {agent} - {reasoning}")
        
        # Reporte final
        final_report = result.get('final_report', '')
        if final_report and not final_report.startswith('Error'):
            print(f"\n📄 REPORTE GENERADO:")
            print("   ✅ Reporte de investigación completado exitosamente")
            print(f"   📏 Longitud: {len(final_report)} caracteres")
            
            # Mostrar preview del reporte si no es muy largo
            if len(final_report) > 1000:
                preview = final_report[:500] + "\n\n... [REPORTE CONTINÚA] ..."
                print(f"\n📖 PREVIEW DEL REPORTE:")
                print("-" * 60)
                print(preview)
                print("-" * 60)
            else:
                print(f"\n📖 REPORTE COMPLETO:")
                print("-" * 60)
                print(final_report)
                print("-" * 60)
        else:
            print("\n❌ ERROR EN LA GENERACIÓN DEL REPORTE")
            print(f"   Detalles: {final_report}")
        
        # Contexto de investigación
        research_context = result.get('research_context', {})
        if research_context:
            print(f"\n🔍 CONTEXTO DE INVESTIGACIÓN:")
            completed = research_context.get('completed_items', 0)
            total = research_context.get('total_items', 0)
            print(f"   • Elementos analizados: {completed}/{total}")
            
            synthesis_notes = research_context.get('synthesis_notes', [])
            if synthesis_notes:
                print(f"   • Notas de síntesis: {len(synthesis_notes)} generadas")
        
        print(f"\n🎯 Estado final: {result.get('next_action', 'COMPLETADO')}")
        print("="*80)
    
    def get_workflow_summary(self) -> dict:
        """Retorna un resumen de la configuración del workflow"""
        return {
            "agents": [
                {"name": "Supervisor", "role": "Coordinación y toma de decisiones"},
                {"name": "Investigador", "role": "Generación de esquemas de investigación"},
                {"name": "Curador", "role": "Análisis profundo y síntesis"},
                {"name": "Reportero", "role": "Generación de reportes finales"}
            ],
            "workflow_stages": [
                "1. Solicitud de tema",
                "2. Generación de esquema",
                "3. Validación humana",
                "4. Curación de contenido",
                "5. Generación de reporte",
                "6. Finalización"
            ],
            "features": [
                "Human-in-the-loop validation",
                "Smart cost optimization", 
                "Multi-source research",
                "Structured reporting",
                "State management"
            ]
        }