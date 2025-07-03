#!/usr/bin/env python3
"""
Prueba del sistema simplificado con 6 opciones
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_agent.workflows.research_workflow import ResearchWorkflow

def test_simplified_system():
    """Prueba el sistema con 6 opciones simples"""
    print("🚀 PRUEBA DEL SISTEMA SIMPLIFICADO")
    print("=" * 60)
    
    # Crear workflow
    workflow = ResearchWorkflow()
    
    # Ejecutar con consulta de prueba
    query = "Inteligencia Artificial en 2024"
    
    print(f"📋 Consulta: {query}")
    print("💡 El sistema ahora genera exactamente 6 opciones simples")
    print("💡 Comandos disponibles:")
    print("   • approve - Aprobar todo")
    print("   • approve 1,3,5 - Aprobar elementos específicos")
    print("   • remove 2,4 - Eliminar elementos")
    print("   • change 1 to \"nuevo título\" - Cambiar título")
    print("   • add \"nuevo elemento\" - Agregar elemento")
    print("   • replace 3 with \"nuevo elemento\" - Reemplazar")
    print("   • reject - Rechazar todo")
    print()
    
    try:
        result = workflow.run(query)
        print("✅ Prueba completada exitosamente")
        return result
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return None

if __name__ == "__main__":
    test_simplified_system() 