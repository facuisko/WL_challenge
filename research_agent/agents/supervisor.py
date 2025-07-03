"""
Agente supervisor que coordina el workflow y maneja interacción con usuario
"""
import re
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.state import ResearchState

class SupervisorAgent(BaseAgent):
    """Supervisor que coordina el flujo de trabajo y maneja validación de índices"""
    
    def __init__(self):
        super().__init__("Supervisor")
    
    def execute(self, state: ResearchState) -> ResearchState:
        """Decide el próximo paso en el workflow"""
        step = state.get('step_count', 0)
        
        # Si no hay user_query, preguntar al usuario qué tema quiere investigar
        if not state.get('user_query'):
            return self._ask_for_research_topic(state)
        
        if step == 0:
            # Primer paso: solicitar índice al investigador
            decision = "GENERATE_OUTLINE"
            self.log("Solicitando índice inicial al investigador")
            return {
                **state,
                "current_agent": self.name,
                "next_action": decision,
                "step_count": step + 1
            }
        
        # Si hay un esquema propuesto y NO está aprobado, seguir interactuando
        if state.get('proposed_outline') and not state.get('outline_approved'):
            return self._interact_with_user(state)
        
        # Si el esquema está aprobado, terminar
        if state.get('outline_approved'):
            decision = "FINISH"
            self.log("✅ Esquema confirmado por usuario - Proceso completado")
            return {
                **state,
                "current_agent": self.name,
                "next_action": decision,
                "step_count": step + 1
            }
        
        # Fallback
        decision = "FINISH"
        self.log("Finalizando proceso")
        return {
            **state,
            "current_agent": self.name,
            "next_action": decision,
            "step_count": step + 1
        }
    
    def _ask_for_research_topic(self, state: ResearchState) -> ResearchState:
        """Pregunta al usuario qué tema quiere investigar"""
        print(f"\n{'='*60}")
        print("🤝 SUPERVISOR: Bienvenido al Sistema de Investigación")
        print(f"{'='*60}")
        print("\n📋 ¿Sobre qué tema te gustaría que investigue?")
        print("💡 Ejemplos:")
        print("   • Inteligencia Artificial en medicina")
        print("   • Cambio climático y energías renovables")
        print("   • Blockchain y criptomonedas")
        print("   • Cualquier tema que te interese...")
        print()
        
        user_topic = input("👤 Tu tema de investigación: ").strip()
        
        if not user_topic:
            print("❌ Por favor, ingresa un tema válido.")
            return self._ask_for_research_topic(state)
        
        self.log(f"🎯 Tema de investigación: {user_topic}")
        
        return {
            **state,
            "user_query": user_topic,
            "current_agent": self.name,
            "step_count": 0  # Reiniciar contador para el nuevo tema
        }
    
    def _interact_with_user(self, state: ResearchState) -> ResearchState:
        """Supervisor maneja interacción simplificada con usuario"""
        outline = state['proposed_outline']
        
        print(f"\n{'='*60}")
        print("🤝 SUPERVISOR: Validación de esquema propuesto")
        print(f"{'='*60}")
        print("\n📋 ESQUEMA PROPUESTO:")
        
        # Mostrar elementos numerados
        outline_items = self._parse_outline_to_items(outline)
        for i, item in enumerate(outline_items, 1):
            print(f"{i}. {item}")
        
        print(f"\n{'='*60}")
        print("💬 COMANDOS DISPONIBLES:")
        print("  • 'approve' - Aprobar todo el esquema")
        print("  • 'approve 1,3,5' - Aprobar solo elementos específicos")
        print("  • 'remove 2,4' - Eliminar elementos específicos")
        print("  • 'change 1 to \"nuevo título\"' - Cambiar título de elemento")
        print("  • 'add \"nuevo elemento\"' - Agregar nuevo elemento")
        print("  • 'reject' - Rechazar todo y regenerar")
        
        user_input = input("\n👤 Tu comando: ").strip()
        
        return self._process_user_command(user_input, state, outline_items)
    
    def _process_user_command(self, command: str, state: ResearchState, outline_items: list) -> ResearchState:
        """Procesa comandos del usuario"""
        command_lower = command.lower()
        
        if command_lower == 'approve':
            # Aprobar todo
            self.log("✅ Esquema aprobado completamente")
            return {
                **state, 
                "outline_approved": True, 
                "current_agent": self.name,
                "outline_items": outline_items
            }
        
        elif command_lower.startswith('approve '):
            # Aprobar elementos específicos
            return self._handle_selective_approval(command, state, outline_items)
        
        elif command_lower.startswith('remove '):
            # Eliminar elementos específicos
            return self._handle_remove_elements(command, state, outline_items)
        
        elif command_lower.startswith('change '):
            # Cambiar título de elemento
            return self._handle_change_title(command, state, outline_items)
        
        elif command_lower.startswith('add '):
            # Agregar nuevo elemento
            return self._handle_add_element(command, state, outline_items)
        
        elif command_lower == 'reject':
            # Rechazar todo - regenerar
            self.log("❌ Esquema rechazado, solicitando regeneración completa")
            return {
                **state, 
                "proposed_outline": "",
                "outline_approved": False,
                "next_action": "GENERATE_OUTLINE",
                "current_agent": self.name,
                "user_feedback": "Regenerar esquema completo"
            }
        
        else:
            print("❌ Comando no reconocido. Intenta de nuevo.")
            return self._interact_with_user(state)
    
    def _parse_outline_to_items(self, outline: str) -> list:
        """Convierte el outline en lista de ítems numerados"""
        lines = outline.split('\n')
        items = []
        for line in lines:
            line = line.strip()
            if line.startswith('###') or line.startswith('##') or (line.startswith('-') and len(line) > 5):
                # Limpiar marcadores markdown
                clean_item = re.sub(r'^#{1,4}\s*', '', line)
                clean_item = re.sub(r'^-\s*', '', clean_item)
                # Eliminar numeración inicial (ej: "1. ", "2. ", etc.)
                clean_item = re.sub(r'^\d+\.\s*', '', clean_item)
                # Excluir líneas que contengan "ESQUEMA DE INVESTIGACIÓN"
                if clean_item and "ESQUEMA DE INVESTIGACIÓN" not in clean_item.upper():
                    items.append(clean_item)
        # Limitar a máximo 6 elementos
        return items[:6]
    
    def _handle_selective_approval(self, command: str, state: ResearchState, outline_items: list) -> ResearchState:
        """Aprobar solo elementos específicos"""
        try:
            numbers_str = command.replace('approve', '').strip()
            approved_indices = [int(x.strip()) - 1 for x in numbers_str.split(',')]
            
            approved_items = [outline_items[i] for i in approved_indices if 0 <= i < len(outline_items)]
            
            self.log(f"✅ Aprobados {len(approved_items)} elementos")
            
            # Regenerar esquema solo con elementos aprobados
            feedback = f"Elementos aprobados: {numbers_str}. Regenerar esquema con estos elementos."
            
            return {
                **state,
                "proposed_outline": "",
                "outline_approved": False,  # NO aprobar aún, continuar loop
                "next_action": "GENERATE_OUTLINE",
                "current_agent": self.name,
                "user_feedback": feedback,
                "outline_items": approved_items
            }
            
        except (ValueError, IndexError) as e:
            print(f"❌ Error en formato: {e}")
            return self._interact_with_user(state)
    
    def _handle_remove_elements(self, command: str, state: ResearchState, outline_items: list) -> ResearchState:
        """Eliminar elementos específicos"""
        try:
            numbers_str = command.replace('remove', '').strip()
            remove_indices = [int(x.strip()) - 1 for x in numbers_str.split(',')]
            
            # Crear nueva lista sin los elementos a eliminar
            remaining_items = [item for i, item in enumerate(outline_items) if i not in remove_indices]
            
            self.log(f"🗑️ Eliminados {len(remove_indices)} elementos")
            
            # Actualizar el esquema directamente sin ir al investigador
            new_outline = self._create_outline_from_items(remaining_items)
            
            return {
                **state,
                "proposed_outline": new_outline,
                "outline_approved": False,
                "next_action": "",  # Quedarse en supervisor
                "current_agent": self.name,
                "outline_items": remaining_items
            }
            
        except (ValueError, IndexError) as e:
            print(f"❌ Error en formato: {e}")
            return self._interact_with_user(state)
    
    def _handle_change_title(self, command: str, state: ResearchState, outline_items: list) -> ResearchState:
        """Cambiar título de elemento específico"""
        try:
            # Parsear: change 1 to "nuevo título"
            match = re.search(r'change\s+(\d+)\s+to\s+["\'](.+)["\']', command)
            if not match:
                match = re.search(r'change\s+(\d+)\s+to\s+(.+)', command)
            
            if not match:
                raise ValueError("Formato incorrecto")
            
            item_num = int(match.group(1)) - 1
            new_title = match.group(2).strip()
            
            if 0 <= item_num < len(outline_items):
                new_items = outline_items.copy()
                old_title = new_items[item_num]
                new_items[item_num] = new_title
                
                self.log(f"🔄 Elemento {item_num + 1} cambiado: '{old_title}' → '{new_title}'")
                
                # Actualizar el esquema directamente sin ir al investigador
                new_outline = self._create_outline_from_items(new_items)
                
                return {
                    **state,
                    "proposed_outline": new_outline,
                    "outline_approved": False,
                    "next_action": "",  # Quedarse en supervisor
                    "current_agent": self.name,
                    "outline_items": new_items
                }
            else:
                print(f"❌ Número de elemento inválido: {item_num + 1}")
                return self._interact_with_user(state)
                
        except (ValueError, AttributeError) as e:
            print(f"❌ Error en formato del comando: {e}")
            print("Formato correcto: 'change 1 to \"nuevo título\"'")
            return self._interact_with_user(state)
    
    def _handle_add_element(self, command: str, state: ResearchState, outline_items: list) -> ResearchState:
        """Agregar nuevo elemento"""
        try:
            # Parsear: add "nuevo elemento"
            match = re.search(r'add\s+["\'](.+)["\']', command)
            if not match:
                match = re.search(r'add\s+(.+)', command)
            
            new_element = match.group(1).strip() if match else "Nuevo elemento"
            
            new_items = outline_items.copy()
            new_items.append(new_element)
            
            self.log(f"➕ Agregado nuevo elemento: {new_element}")
            
            # Actualizar el esquema directamente sin ir al investigador
            new_outline = self._create_outline_from_items(new_items)
            
            return {
                **state,
                "proposed_outline": new_outline,
                "outline_approved": False,
                "next_action": "",  # Quedarse en supervisor
                "current_agent": self.name,
                "outline_items": new_items
            }
            
        except AttributeError as e:
            print(f"❌ Error en formato: {e}")
            return self._interact_with_user(state)
    
    def _create_outline_from_items(self, items: list) -> str:
        """Crea un esquema formateado a partir de una lista de elementos"""
        outline = "## ESQUEMA DE INVESTIGACIÓN\n\n"
        for i, item in enumerate(items, 1):
            outline += f"### {i}. {item}\n\n"
        return outline 