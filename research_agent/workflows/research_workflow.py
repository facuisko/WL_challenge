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
        
        # Punto de entrada
        workflow.set_entry_point("supervisor")
        
        # Edges condicionales desde supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "investigator": "investigator",
                "continue": "supervisor",  # Volver al supervisor
                "end": END
            }
        )
        
        # Después del investigador, volver al supervisor
        workflow.add_edge("investigator", "supervisor")
        
        return workflow.compile()
    
    def _route_from_supervisor(self, state: ResearchState) -> str:
        """Enruta desde el supervisor"""
        action = state.get('next_action')
        
        if action == "GENERATE_OUTLINE":
            return "investigator"
        elif action == "FINISH":
            return "end"
        else:
            # Si no hay acción específica, continuar con el supervisor
            return "continue"
    
    def run(self, user_query: str = None) -> ResearchState:
        """Ejecuta el workflow completo"""
        initial_state = {
            "user_query": user_query,  # Puede ser None para que el supervisor pregunte
            "proposed_outline": "",
            "outline_approved": False,
            "outline_items": [],          # NUEVO
            "user_feedback": "",          # NUEVO
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