"""
Punto de entrada principal del sistema agéntico de investigación completo
"""
import os
from research_agent.workflows.agentic_workflow import AgenticResearchWorkflow
from research_agent.config.settings import Settings

def main():
    """Función principal del sistema agéntico"""
    print("🚀 SISTEMA AGÉNTICO DE INVESTIGACIÓN")
    print("=" * 60)
    print("🤖 Resolución completa del Challenge con múltiples agentes")
    print("=" * 60)
    
    # Verificar configuración
    if not Settings.validate_config():
        print("❌ Error: Configuración incompleta")
        print("💡 Asegúrate de configurar OPENAI_API_KEY")
        return
    
    print("✅ Configuración validada")
    
    # Crear workflow agéntico completo
    try:
        workflow = AgenticResearchWorkflow()
        print("✅ Workflow agéntico inicializado")
        
        # Mostrar resumen del sistema
        summary = workflow.get_workflow_summary()
        print(f"\n📋 AGENTES DISPONIBLES:")
        for agent in summary["agents"]:
            print(f"   🤖 {agent['name']}: {agent['role']}")
        
        print(f"\n🔄 ETAPAS DEL WORKFLOW:")
        for stage in summary["workflow_stages"]:
            print(f"   📊 {stage}")
        
        print(f"\n⚡ CARACTERÍSTICAS:")
        for feature in summary["features"]:
            print(f"   ✨ {feature}")
        
    except Exception as e:
        print(f"❌ Error inicializando workflow: {e}")
        print("🔧 Revisa las dependencias y configuración")
        return
    
    print("\n" + "=" * 60)
    print("🎯 INICIANDO PROCESO DE INVESTIGACIÓN")
    print("=" * 60)
    
    # Ejecutar workflow completo
    # El tema se preguntará interactivamente si no se especifica
    try:
        result = workflow.run()
        
        # El workflow ya muestra los resultados, aquí solo confirmamos
        if result.get('final_report') and not result['final_report'].startswith('Error'):
            print("\n🎉 ¡INVESTIGACIÓN COMPLETADA EXITOSAMENTE!")
            
            # Opción para guardar el reporte
            save_report = input("\n💾 ¿Deseas guardar el reporte en un archivo? (s/n): ").lower().strip()
            if save_report == 's':
                save_report_to_file(result)
        else:
            print("\n❌ Hubo problemas durante la investigación")
            print("🔧 Revisa los logs para más detalles")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Proceso interrumpido por el usuario")
        print("👋 ¡Gracias por usar el Sistema Agéntico de Investigación!")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        print("🔧 Revisa la configuración y las dependencias")

def save_report_to_file(result):
    """Guarda el reporte final en un archivo"""
    try:
        # Crear nombre de archivo basado en el tema
        topic = result.get('user_query', 'investigacion')
        filename = f"reporte_{topic.replace(' ', '_').lower()}.md"
        
        # Limpiar caracteres especiales del nombre de archivo
        import re
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        
        # Escribir reporte
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result['final_report'])
        
        print(f"✅ Reporte guardado como: {filename}")
        
        # Mostrar estadísticas del archivo
        file_size = os.path.getsize(filename)
        print(f"📏 Tamaño del archivo: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")

def demo_mode():
    """Modo demo con tema predefinido para pruebas"""
    print("🧪 MODO DEMO - Tema predefinido para pruebas")
    
    # Verificar configuración
    if not Settings.validate_config():
        print("❌ Error: Configuración incompleta para demo")
        return
    
    # Tema de demo
    demo_topic = "Inteligencia Artificial aplicada a medicina"
    
    try:
        workflow = AgenticResearchWorkflow()
        print(f"🎯 Ejecutando demo con tema: {demo_topic}")
        
        # Ejecutar con tema predefinido
        result = workflow.run(user_query=demo_topic)
        
        if result.get('final_report'):
            print("\n🎉 Demo completado exitosamente")
            return result
        else:
            print("\n❌ Demo falló")
            
    except Exception as e:
        print(f"❌ Error en demo: {e}")

def auto_demo_mode():
    """Modo demo completamente automático que simula aprobaciones"""
    print("🤖 MODO DEMO AUTOMÁTICO - Sin intervención humana")
    
    # Verificar configuración
    if not Settings.validate_config():
        print("❌ Error: Configuración incompleta para demo automático")
        return
    
    # Tema de demo
    demo_topic = "Inteligencia Artificial aplicada a medicina"
    
    try:
        workflow = AgenticResearchWorkflow()
        print(f"🎯 Ejecutando demo automático con tema: {demo_topic}")
        
        # Simular aprobaciones automáticas
        workflow.set_auto_approve_mode(True)
        
        # Ejecutar con tema predefinido
        result = workflow.run(user_query=demo_topic)
        
        if result.get('final_report'):
            print("\n🎉 Demo automático completado exitosamente")
            return result
        else:
            print("\n❌ Demo automático falló")
            
    except Exception as e:
        print(f"❌ Error en demo automático: {e}")

if __name__ == "__main__":
    import sys
    
    # Verificar si se quiere ejecutar en modo demo
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_mode()
        elif sys.argv[1] == "auto":
            auto_demo_mode()
        else:
            main()
    else:
        main()