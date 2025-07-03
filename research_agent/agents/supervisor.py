"""
Agente supervisor que coordina el workflow
"""
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.state import ResearchState

class SupervisorAgent(BaseAgent):
    """Supervisor que coordina el flujo de trabajo"""
    
    def __init__(self):
        super().__init__("Supervisor")
    
    def execute(self, state: ResearchState) -> ResearchState:
        """Decide el próximo paso en el workflow"""
        step = state.get('step_count', 0)
        
        if step == 0:
            # Primer paso: generar esquema
            decision = "GENERATE_OUTLINE"
            self.log("Iniciando proceso de investigación")
            
        elif not state.get('outline_approved', False):
            # Esperar aprobación del cliente
            decision = "WAIT_APPROVAL"
            self.log("Esperando aprobación del esquema de investigación")
            
        elif state.get('outline_approved', False) and not state.get('research_results'):
            # Continuar con investigación
            decision = "CONDUCT_RESEARCH"
            self.log("Esquema aprobado, iniciando investigación detallada")
            
        else:
            # Finalizar
            decision = "FINISH"
            self.log("Proceso de investigación completado")
        
        return {
            **state,
            "current_agent": self.name,
            "next_action": decision,
            "step_count": step + 1
        } 