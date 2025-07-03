#!/usr/bin/env python3
"""
Prueba del sistema con tema libre
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_agent.workflows.research_workflow import ResearchWorkflow

def test_free_topic():
    """Prueba el sistema con tema libre"""
    print("🚀 SISTEMA DE INVESTIGACIÓN CON TEMA LIBRE")
    print("=" * 60)
    print("💡 El supervisor te preguntará qué tema quieres investigar")
    print("💡 Luego podrás modificar el esquema hasta que estés conforme")
    print()
    
    # Crear workflow
    workflow = ResearchWorkflow()
    
    try:
        # Ejecutar sin tema predefinido - el supervisor preguntará
        result = workflow.run()
        print("✅ Proceso completado exitosamente")
        return result
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
        return None

if __name__ == "__main__":
    test_free_topic() 