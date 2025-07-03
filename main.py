"""
Punto de entrada principal del sistema de agentes de investigación
"""
import os
from research_agent.workflows.research_workflow import ResearchWorkflow
from research_agent.config.settings import Settings

def main():
    """Función principal"""
    print("🚀 SISTEMA DE AGENTES DE INVESTIGACIÓN")
    print("=" * 60)
    
    # Verificar configuración
    if not Settings.validate_config():
        print("❌ Error: Configuración incompleta")
        return
    
    # Crear workflow
    workflow = ResearchWorkflow()
    
    # Consulta de ejemplo
    user_query = "Investigá las tendencias actuales en inteligencia artificial aplicada a medicina"
    
    print(f"\n📋 CONSULTA: {user_query}")
    print("=" * 60)
    
    # Ejecutar workflow
    result = workflow.run(user_query)
    
    print("=" * 60)
    print("✅ Proceso completado")

if __name__ == "__main__":
    main() 