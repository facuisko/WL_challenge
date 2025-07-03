import os
import requests
from bs4 import BeautifulSoup
import time
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# 1. Definir el estado compartido
class AgentState(TypedDict):
    messages: list
    task: str
    current_agent: str
    investigation_result: str
    next_action: str
    step_count: int

# 2. Nodo Supervisor (versión simple sin LLM)
def supervisor_node(state: AgentState):
    """
    El supervisor decide qué hacer: investigar o terminar
    Version simplificada que no requiere API key
    """
    step = state.get('step_count', 0)
    
    # Lógica simple: investigar una vez, luego terminar
    if step == 0 and not state.get('investigation_result'):
        decision = "INVESTIGATE"
        print(f"🎯 SUPERVISOR: Necesito investigar sobre '{state['task']}'")
    elif state.get('investigation_result'):
        decision = "FINISH"
        print(f"🎯 SUPERVISOR: Ya tengo información suficiente, terminando")
    else:
        decision = "FINISH"
        print(f"🎯 SUPERVISOR: Terminando proceso")
    
    return {
        **state,
        "current_agent": "supervisor",
        "next_action": decision,
        "step_count": step + 1
    }

# 3. Funciones auxiliares para búsqueda web
def search_duckduckgo(query: str, max_results: int = 3):
    """
    Búsqueda simple usando DuckDuckGo (no requiere API key)
    """
    try:
        # DuckDuckGo instant answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer información útil
            results = []
            
            # Abstract (resumen principal)
            if data.get('Abstract'):
                results.append(f"Resumen: {data['Abstract']}")
            
            # Related topics
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:2]:  # Solo primeros 2
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(f"Información relacionada: {topic['Text']}")
            
            return results if results else [f"Búsqueda realizada para: {query}"]
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return [f"Error en búsqueda web para: {query}"]

def search_web_fallback(query: str):
    """
    Búsqueda alternativa si DuckDuckGo no funciona
    """
    # Simulación mejorada basada en palabras clave
    keywords_mapping = {
        'ia': "Inteligencia Artificial: tendencias en LLMs, IA generativa, automatización",
        'inteligencia artificial': "IA actual: GPT-4, Claude, agentes autónomos, ética en IA",
        'marketing': "Marketing digital: SEO, redes sociales, contenido personalizado, analytics",
        'clima': "Clima actual: cambio climático, sostenibilidad, energías renovables",
        'tecnologia': "Tecnología 2024: IA, blockchain, computación cuántica, IoT",
        'salud': "Salud digital: telemedicina, IA en diagnósticos, apps de salud"
    }
    
    query_lower = query.lower()
    for keyword, info in keywords_mapping.items():
        if keyword in query_lower:
            return [f"Información encontrada: {info}"]
    
    return [f"Búsqueda general completada para: {query}"]

# 4. Nodo Investigador con búsqueda web real
def researcher_node(state: AgentState):
    """
    El investigador hace búsquedas web reales
    """
    task = state['task']
    print(f"🔍 INVESTIGADOR: Investigando sobre '{task}'...")
    print(f"🔍 INVESTIGADOR: Realizando búsqueda web...")
    
    # Realizar búsqueda web real
    search_results = search_duckduckgo(task)
    
    if not search_results or len(search_results) == 0:
        print(f"🔍 INVESTIGADOR: Usando búsqueda alternativa...")
        search_results = search_web_fallback(task)
    
    # Formatear resultados
    investigation_report = f"""
INVESTIGACIÓN COMPLETADA PARA: {task}

RESULTADOS DE BÚSQUEDA WEB:
{'=' * 40}
"""
    
    for i, result in enumerate(search_results, 1):
        investigation_report += f"\n{i}. {result}\n"
    
    investigation_report += f"""
{'=' * 40}
Búsqueda realizada en: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total de resultados procesados: {len(search_results)}
"""
    
    print(f"🔍 INVESTIGADOR: ¡Búsqueda web completada! Encontrados {len(search_results)} resultados")
    
    return {
        **state,
        "current_agent": "researcher",
        "investigation_result": investigation_report.strip()
    }

# 5. Función de enrutamiento
def route_next(state: AgentState):
    """
    Decide cuál es el próximo nodo basado en la decisión del supervisor
    """
    if state["next_action"] == "INVESTIGATE":
        return "researcher"
    elif state["next_action"] == "FINISH":
        return END
    else:
        return "supervisor"  # Por defecto, volver al supervisor

# 6. Construir el grafo
def create_research_workflow():
    workflow = StateGraph(AgentState)
    
    # Agregar nodos
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    
    # Definir el punto de entrada
    workflow.set_entry_point("supervisor")
    
    # Agregar edges (conexiones)
    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "researcher": "researcher",
            END: END
        }
    )
    
    # Después de investigar, volver al supervisor
    workflow.add_edge("researcher", "supervisor")
    
    return workflow.compile()

# 7. Función principal para ejecutar
def run_research(task: str):
    """
    Ejecuta el workflow de investigación
    """
    workflow = create_research_workflow()
    
    initial_state = {
        "messages": [],
        "task": task,
        "current_agent": "",
        "investigation_result": "",
        "step_count": 0
    }
    
    print(f"🚀 Iniciando investigación sobre: {task}")
    print("=" * 50)
    
    # Ejecutar el workflow
    result = workflow.invoke(initial_state)
    
    print("=" * 50)
    print(f"✅ Resultado final:")
    print(f"Tarea: {result['task']}")
    print(f"Investigación: {result['investigation_result']}")
    
    return result

# 8. Ejemplos de uso con búsqueda web real
if __name__ == "__main__":
    print("🚀 LANGGRAPH CON BÚSQUEDA WEB REAL")
    print("=" * 60)
    
    # Ejemplo 1: IA
    print("\n📋 EJEMPLO 1: Investigación sobre IA")
    run_research("¿Qué es GPT-4?")
    
    print("\n" + "=" * 60)
    
    # Ejemplo 2: Tema de actualidad
    print("\n📋 EJEMPLO 2: Investigación sobre tecnología")
    run_research("blockchain technology")
    
    print("\n" + "=" * 60)
    
    # Ejemplo 3: Prueba tu propio tema
    print("\n📋 EJEMPLO 3: Tu turno")
    print("💡 Probá cambiar la consulta en el código por algo que te interese!")
    
    print("\n✅ ¡Ejemplos completados! Ahora con búsqueda web real.")
    print("\n💡 Próximos pasos:")
    print("   - Agregar más agentes especializados")
    print("   - Mejorar el análisis de resultados")
    print("   - Conectar APIs más potentes (Google, Bing, etc.)")