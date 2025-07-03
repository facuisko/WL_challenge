"""
Workflow principal de investigación usando LangGraph
"""
from langgraph.graph import StateGraph, END
from research_agent.models.state import ResearchState
from research_agent.agents.supervisor import SupervisorAgent
from research_agent.agents.investigator import InvestigatorAgent

class ResearchWorkflow:
    """Workflow principal de investigación"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.investigator = InvestigatorAgent()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Crea el grafo de LangGraph"""
        workflow = StateGraph(ResearchState)
        
        # Agregar nodos
        workflow.add_node("supervisor", self.supervisor.execute)
        workflow.add_node("investigator", self.investigator.execute)
        workflow.add_node("human_approval", self._human_approval_node)
        
        # Punto de entrada
        workflow.set_entry_point("supervisor")
        
        # Edges condicionales
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "investigator": "investigator",
                "human_approval": "human_approval",
                "end": END
            }
        )
        
        # Después del investigador, volver al supervisor
        workflow.add_edge("investigator", "supervisor")
        
        # Después de aprobación humana, volver al supervisor
        workflow.add_edge("human_approval", "supervisor")
        
        return workflow.compile()
    
    def _route_from_supervisor(self, state: ResearchState) -> str:
        """Enruta desde el supervisor"""
        action = state.get('next_action')
        
        if action == "GENERATE_OUTLINE" or action == "CONDUCT_RESEARCH":
            return "investigator"
        elif action == "WAIT_APPROVAL":
            return "human_approval"
        elif action == "FINISH":
            return "end"
        else:
            return "investigator"
    
    def _human_approval_node(self, state: ResearchState) -> ResearchState:
        """Nodo para aprobación humana"""
        print("\n" + "="*60)
        print("🤝 VALIDACIÓN HUMANA REQUERIDA")
        print("="*60)
        
        # Mostrar esquema propuesto
        outline = state.get('proposed_outline', 'No hay esquema disponible')
        print("\n📋 ESQUEMA DE INVESTIGACIÓN PROPUESTO:")
        print(outline)
        
        print("\n" + "="*60)
        print("¿Aprobás este esquema de investigación?")
        print("Opciones:")
        print("  [s] Sí, continuar con este esquema")
        print("  [n] No, necesita modificaciones")
        print("  [q] Cancelar investigación")
        
        # Simulación de input humano (en una app real sería interactivo)
        # Por ahora, auto-aprobar para testing
        user_input = input("\nTu decisión [s/n/q]: ").lower().strip()
        
        if user_input == 's' or user_input == '':
            print("✅ Esquema aprobado, continuando con investigación...")
            approved = True
        elif user_input == 'q':
            print("❌ Investigación cancelada por el usuario")
            return {**state, "next_action": "FINISH", "outline_approved": False}
        else:
            print("❌ Esquema rechazado. En una versión completa, aquí se permitiría modificar el esquema.")
            approved = False
        
        return {
            **state,
            "outline_approved": approved,
            "current_agent": "human"
        }
    
    def run(self, user_query: str) -> ResearchState:
        """Ejecuta el workflow completo"""
        initial_state = {
            "user_query": user_query,
            "proposed_outline": "",
            "outline_approved": False,
            "current_agent": "",
            "next_action": "",
            "research_results": {},
            "final_report": "",
            "step_count": 0,
            "conversation_history": []
        }
        
        # Ejecutar workflow
        result = self.workflow.invoke(initial_state)
        
        # Mostrar resultados finales
        self._display_final_results(result)
        
        return result
    
    def _display_final_results(self, result: ResearchState):
        """Muestra los resultados finales"""
        print("\n" + "="*60)
        print("📊 RESULTADOS FINALES")
        print("="*60)
        
        print(f"\n📋 Consulta original: {result['user_query']}")
        
        if result.get('research_results'):
            print(f"\n🔍 Investigación completada:")
            for key, value in result['research_results'].items():
                print(f"\n{value}")
        
        print(f"\n📈 Pasos ejecutados: {result.get('step_count', 0)}")
        print(f"✅ Estado final: {result.get('current_agent', 'Desconocido')}") 