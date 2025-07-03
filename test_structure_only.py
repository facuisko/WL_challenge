#!/usr/bin/env python3
"""
Prueba de estructura del sistema simplificado (sin OpenAI)
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_structure():
    """Prueba la estructura del sistema"""
    print("🔍 PRUEBA DE ESTRUCTURA DEL SISTEMA")
    print("=" * 50)
    
    try:
        # Importar módulos
        from research_agent.models.state import ResearchState
        from research_agent.agents.supervisor import SupervisorAgent
        from research_agent.agents.investigator import InvestigatorAgent
        from research_agent.workflows.research_workflow import ResearchWorkflow
        
        print("✅ Todos los módulos importados correctamente")
        
        # Crear instancias
        supervisor = SupervisorAgent()
        investigator = InvestigatorAgent()
        
        print("✅ Agentes creados correctamente")
        
        # Crear estado de prueba
        test_state = {
            "user_query": "Test query",
            "proposed_outline": "",
            "outline_approved": False,
            "outline_items": [],
            "user_feedback": "",
            "current_agent": "",
            "next_action": "",
            "research_results": {},
            "final_report": "",
            "step_count": 0,
            "conversation_history": []
        }
        
        print("✅ Estado de prueba creado")
        
        # Probar parsing de outline
        test_outline = """
        ## ESQUEMA DE INVESTIGACIÓN
        
        ### 1. Introducción a la IA
        ### 2. Aplicaciones Prácticas
        ### 3. Desafíos Éticos
        ### 4. Tendencias Actuales
        ### 5. Impacto en la Sociedad
        ### 6. Futuro de la IA
        """
        
        items = supervisor._parse_outline_to_items(test_outline)
        print(f"✅ Parsing de outline: {len(items)} elementos encontrados")
        for i, item in enumerate(items, 1):
            print(f"   {i}. {item}")
        
        # Probar comandos
        print("\n🧪 PRUEBA DE COMANDOS:")
        
        # Comando approve
        result = supervisor._process_user_command("approve", test_state, items)
        print(f"✅ Comando 'approve': {result.get('outline_approved', False)}")
        
        # Comando approve específico
        result = supervisor._process_user_command("approve 1,3,5", test_state, items)
        approved_items = result.get('outline_items', [])
        print(f"✅ Comando 'approve 1,3,5': {len(approved_items)} elementos aprobados")
        
        # Comando remove
        result = supervisor._process_user_command("remove 2,4", test_state, items)
        remaining_items = result.get('outline_items', [])
        print(f"✅ Comando 'remove 2,4': {len(remaining_items)} elementos restantes")
        
        # Comando change
        result = supervisor._process_user_command('change 1 to "Nuevo título"', test_state, items)
        feedback = result.get('user_feedback', '')
        print(f"✅ Comando 'change': {feedback}")
        
        # Comando add
        result = supervisor._process_user_command('add "Nuevo elemento"', test_state, items)
        new_items = result.get('outline_items', [])
        print(f"✅ Comando 'add': {len(new_items)} elementos totales")
        
        # Comando replace
        result = supervisor._process_user_command('replace 3 with "Elemento reemplazado"', test_state, items)
        feedback = result.get('user_feedback', '')
        print(f"✅ Comando 'replace': {feedback}")
        
        print("\n🎉 ¡Todas las pruebas de estructura pasaron!")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de estructura: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_structure() 