"""
Script de prueba para verificar el sistema de agentes de investigación
"""
import os
import sys

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente"""
    print("🧪 Probando imports...")
    
    try:
        from research_agent.config.settings import Settings
        print("✅ Settings importado correctamente")
        
        from research_agent.models.state import ResearchState
        print("✅ ResearchState importado correctamente")
        
        from research_agent.agents.base_agent import BaseAgent
        print("✅ BaseAgent importado correctamente")
        
        from research_agent.agents.supervisor import SupervisorAgent
        print("✅ SupervisorAgent importado correctamente")
        
        from research_agent.agents.investigator import InvestigatorAgent
        print("✅ InvestigatorAgent importado correctamente")
        
        from research_agent.tools.openai_client import OpenAIClient
        print("✅ OpenAIClient importado correctamente")
        
        from research_agent.workflows.research_workflow import ResearchWorkflow
        print("✅ ResearchWorkflow importado correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_configuration():
    """Prueba la configuración del sistema"""
    print("\n🔧 Probando configuración...")
    
    from research_agent.config.settings import Settings
    
    # Verificar si hay API key configurada
    if Settings.OPENAI_API_KEY:
        print("✅ OpenAI API Key configurada")
        return True
    else:
        print("⚠️  OpenAI API Key no configurada")
        print("💡 Configurala con: export OPENAI_API_KEY='tu-key'")
        return False

def test_workflow_creation():
    """Prueba la creación del workflow"""
    print("\n🔄 Probando creación de workflow...")
    
    try:
        from research_agent.workflows.research_workflow import ResearchWorkflow
        
        workflow = ResearchWorkflow()
        print("✅ Workflow creado correctamente")
        
        # Verificar que los agentes estén inicializados
        if hasattr(workflow, 'supervisor') and hasattr(workflow, 'investigator'):
            print("✅ Agentes inicializados correctamente")
            return True
        else:
            print("❌ Agentes no inicializados correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error creando workflow: {e}")
        return False

def test_basic_functionality():
    """Prueba funcionalidad básica sin OpenAI"""
    print("\n🎯 Probando funcionalidad básica...")
    
    try:
        from research_agent.agents.supervisor import SupervisorAgent
        from research_agent.models.state import ResearchState
        
        # Crear estado inicial
        initial_state = {
            "user_query": "Test query",
            "proposed_outline": "",
            "outline_approved": False,
            "current_agent": "",
            "next_action": "",
            "research_results": {},
            "final_report": "",
            "step_count": 0,
            "conversation_history": []
        }
        
        # Probar supervisor
        supervisor = SupervisorAgent()
        result = supervisor.execute(initial_state)
        
        if result.get('next_action') == "GENERATE_OUTLINE":
            print("✅ Supervisor funciona correctamente")
            return True
        else:
            print("❌ Supervisor no funciona como esperado")
            return False
            
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuración", test_configuration),
        ("Creación de Workflow", test_workflow_creation),
        ("Funcionalidad Básica", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} falló")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
        print("\n💡 Para ejecutar el sistema completo:")
        print("   1. Configura tu OPENAI_API_KEY")
        print("   2. Ejecuta: python main.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 