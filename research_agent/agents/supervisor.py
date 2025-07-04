"""
Agente supervisor que coordina el workflow completo multi-agente
"""
import re
from research_agent.agents.base_agent import BaseAgent
from research_agent.models.agentic_state import AgenticResearchState

class SupervisorAgent(BaseAgent):
    """Supervisor que coordina el flujo de trabajo completo con múltiples agentes"""
    
    def __init__(self):
        super().__init__("Supervisor")
    
    def execute(self, state: AgenticResearchState) -> AgenticResearchState:
        """Decide el próximo paso en el workflow completo"""
        step = state.get('step_count', 0)
        current_stage = self._determine_current_stage(state)
        
        self.log(f"📋 Evaluando estado - Paso {step}, Etapa: {current_stage}")
        
        # Etapa 1: Solicitar tema de investigación
        if not state.get('user_query'):
            return self._ask_for_research_topic(state)
        
        # Etapa 2: Generar esquema inicial
        if current_stage == "INITIAL":
            decision = "GENERATE_OUTLINE"
            reasoning = "Iniciando proceso con generación de esquema"
            self.log("🎯 Solicitando esquema inicial al investigador")
            return self._update_state_with_decision(state, decision, reasoning, step + 1)
        
        # Etapa 3: Validación humana del esquema
        if current_stage == "OUTLINE_PENDING":
            return self._interact_with_user(state)
        
        # Etapa 4: Curación profunda del contenido aprobado
        if current_stage == "OUTLINE_APPROVED":
            decision = "CURATE_CONTENT"
            reasoning = "Esquema aprobado, iniciando curación profunda"
            self.log("🔍 Enviando contenido aprobado al curador")
            return self._update_state_with_decision(state, decision, reasoning, step + 1)
        
        # Etapa 5: Generación del reporte final
        if current_stage == "CONTENT_CURATED":
            decision = "GENERATE_REPORT"
            reasoning = "Contenido curado, generando reporte final"
            self.log("📄 Enviando al reportero para reporte final")
            return self._update_state_with_decision(state, decision, reasoning, step + 1)
        
        # Etapa 6: Finalización
        if current_stage == "REPORT_READY":
            decision = "FINISH"
            reasoning = "Proceso completado exitosamente"
            self.log("✅ Proceso de investigación completado")
            return self._update_state_with_decision(state, decision, reasoning, step + 1)
        
        # Fallback - algo salió mal
        decision = "FINISH"
        reasoning = "Estado no reconocido, finalizando proceso"
        self.log(f"⚠️ Estado no reconocido: {current_stage}, finalizando")
        return self._update_state_with_decision(state, decision, reasoning, step + 1)
    
    def _determine_current_stage(self, state: AgenticResearchState) -> str:
        """Determina la etapa actual del workflow"""
        
        # Si hay reporte final, proceso completado
        if state.get('final_report'):
            return "REPORT_READY"
        
        # Si hay análisis completado, listo para reporte
        if state.get('analysis_complete'):
            return "CONTENT_CURATED"
        
        # Si el esquema está aprobado, listo para curación
        if state.get('outline_approved'):
            return "OUTLINE_APPROVED"
        
        # Si hay esquema propuesto pero no aprobado
        if state.get('proposed_outline') and not state.get('outline_approved'):
            return "OUTLINE_PENDING"
        
        # Estado inicial
        return "INITIAL"
    
    def _update_state_with_decision(self, state: AgenticResearchState, decision: str, 
                                   reasoning: str, new_step: int) -> AgenticResearchState:
        """Actualiza el estado con una nueva decisión"""
        return {
            **state,
            "current_agent": self.name,
            "next_action": decision,
            "supervisor_reasoning": reasoning,
            "step_count": new_step,
            "agent_decisions": {
                **state.get("agent_decisions", {}),
                f"step_{new_step}": {
                    "agent": self.name,
                    "decision": decision,
                    "reasoning": reasoning,
                    "timestamp": f"step_{new_step}"
                }
            }
        }
    
    def _ask_for_research_topic(self, state: AgenticResearchState) -> AgenticResearchState:
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
            "step_count": 0,  # Reiniciar contador para el nuevo tema
            "current_research_topic": user_topic,
            "research_context": {},
            "agent_decisions": {},
            "autonomous_actions": [],
            "quality_assessments": {},
            "inter_agent_messages": []
        }
    
    def _interact_with_user(self, state: AgenticResearchState) -> AgenticResearchState:
        """Supervisor maneja interacción simplificada con usuario"""
        outline = state['proposed_outline']
        
        print(f"\n{'='*60}")
        print("🤝 SUPERVISOR: Validación de esquema propuesto")
        print(f"{'='*60}")
        print("\n📋 ESQUEMA PROPUESTO:")
        
        # Usar outline_items del estado si está disponible, sino parsear
        if 'outline_items' in state and state['outline_items']:
            outline_items = state['outline_items']
        else:
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
        print("  • 'reject 2, add \"new item\"' - Comando compuesto")
        print("  • 'modify 1 to \"new title\"' - Alias para change")
        
        user_input = input("\n👤 Tu comando: ").strip()
        
        return self._process_user_command(user_input, state, outline_items)
    
    def _process_user_command(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
        """Procesa comandos del usuario, incluyendo comandos compuestos"""
        # Primero verificar si es un comando compuesto (contiene comas)
        if ',' in command and not command.lower().startswith('approve ') and not command.lower().startswith('remove '):
            return self._handle_compound_command(command, state, outline_items)
        
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
        
        elif command_lower.startswith('change ') or command_lower.startswith('modify '):
            # Cambiar título de elemento (change o modify)
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
    
    def _handle_selective_approval(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
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
    
    def _handle_remove_elements(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
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
    
    def _handle_change_title(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
        """Cambiar título de elemento específico (soporta 'change' y 'modify')"""
        try:
            # Parsear: change/modify 1 to "nuevo título" o change/modify 1 to 'nuevo título'
            # Primero intentar con comillas dobles
            match = re.search(r'(?:change|modify)\s+(\d+)\s+to\s+"([^"]+)"', command)
            if not match:
                # Intentar con comillas simples
                match = re.search(r"(?:change|modify)\s+(\d+)\s+to\s+'([^']+)'", command)
            if not match:
                # Sin comillas, tomar todo después de "to "
                match = re.search(r'(?:change|modify)\s+(\d+)\s+to\s+(.+)', command)
            
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
            print("Formato correcto: 'change 1 to \"nuevo título\"' o 'change 1 to nuevo título'")
            return self._interact_with_user(state)
    
    def _handle_add_element(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
        """Agregar nuevo elemento"""
        try:
            # Parsear: add "nuevo elemento" o add 'nuevo elemento'
            # Primero intentar con comillas dobles
            match = re.search(r'add\s+"([^"]+)"', command)
            if not match:
                # Intentar con comillas simples
                match = re.search(r"add\s+'([^']+)'", command)
            if not match:
                # Sin comillas, tomar todo después de "add "
                match = re.search(r'add\s+(.+)', command)
            
            if match:
                new_element = match.group(1).strip()
            else:
                new_element = "Nuevo elemento"
            
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
            
        except Exception as e:
            print(f"❌ Error procesando comando add: {e}")
            return self._interact_with_user(state)
    
    def _create_outline_from_items(self, items: list) -> str:
        """Crea un esquema formateado a partir de una lista de elementos"""
        outline = "## ESQUEMA DE INVESTIGACIÓN\n\n"
        for i, item in enumerate(items, 1):
            outline += f"### {i}. {item}\n\n"
        return outline
    
    def _handle_compound_command(self, command: str, state: AgenticResearchState, outline_items: list) -> AgenticResearchState:
        """
        Maneja comandos compuestos como 'reject 2, add "new item"'
        Ejemplos del challenge:
        - "reject 2, add 'AI safety concerns'"
        - "modify 1 to 'AI ethical frameworks'"
        """
        self.log(f"🔄 Procesando comando compuesto: {command}")
        
        # Dividir por comas y procesar cada parte
        parts = [part.strip() for part in command.split(',')]
        current_items = outline_items.copy()
        current_state = state
        
        for i, part in enumerate(parts):
            self.log(f"   📋 Ejecutando parte {i+1}: '{part}'")
            
            # Crear estado temporal para esta parte del comando
            temp_state = {
                **current_state,
                "outline_items": current_items
            }
            
            # Procesar esta parte del comando
            if part.lower().startswith('reject '):
                # Extract number and remove that item
                try:
                    reject_match = re.search(r'reject\s+(\d+)', part)
                    if reject_match:
                        item_num = int(reject_match.group(1)) - 1
                        if 0 <= item_num < len(current_items):
                            removed_item = current_items.pop(item_num)
                            self.log(f"   🗑️ Eliminado elemento {item_num + 1}: '{removed_item}'")
                        else:
                            print(f"   ❌ Número de elemento inválido: {item_num + 1}")
                except (ValueError, IndexError):
                    print(f"   ❌ Error procesando 'reject' en: {part}")
            
            elif part.lower().startswith('add '):
                # Agregar elemento
                try:
                    # Usar el mismo parsing que el método individual
                    match = re.search(r'add\s+"([^"]+)"', part)
                    if not match:
                        match = re.search(r"add\s+'([^']+)'", part)
                    if not match:
                        match = re.search(r'add\s+(.+)', part)
                    
                    if match:
                        new_element = match.group(1).strip()
                        current_items.append(new_element)
                        self.log(f"   ➕ Agregado: '{new_element}'")
                except Exception as e:
                    print(f"   ❌ Error procesando 'add' en: {part}")
            
            elif part.lower().startswith('modify ') or part.lower().startswith('change '):
                # Modificar elemento
                try:
                    # Usar el mismo parsing que el método individual
                    match = re.search(r'(?:modify|change)\s+(\d+)\s+to\s+"([^"]+)"', part)
                    if not match:
                        match = re.search(r"(?:modify|change)\s+(\d+)\s+to\s+'([^']+)'", part)
                    if not match:
                        match = re.search(r'(?:modify|change)\s+(\d+)\s+to\s+(.+)', part)
                    
                    if match:
                        item_num = int(match.group(1)) - 1
                        new_title = match.group(2).strip()
                        if 0 <= item_num < len(current_items):
                            old_title = current_items[item_num]
                            current_items[item_num] = new_title
                            self.log(f"   🔄 Cambiado elemento {item_num + 1}: '{old_title}' → '{new_title}'")
                        else:
                            print(f"   ❌ Número de elemento inválido: {item_num + 1}")
                except (ValueError, IndexError):
                    print(f"   ❌ Error procesando 'modify/change' en: {part}")
            
            else:
                print(f"   ⚠️ Comando no reconocido en parte: '{part}'")
        
        # Actualizar el esquema con todos los cambios aplicados
        new_outline = self._create_outline_from_items(current_items)
        
        self.log(f"✅ Comando compuesto completado. {len(current_items)} elementos finales")
        
        return {
            **state,
            "proposed_outline": new_outline,
            "outline_approved": False,
            "next_action": "",  # Quedarse en supervisor
            "current_agent": self.name,
            "outline_items": current_items
        } 