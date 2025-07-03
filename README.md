# Sistema de Agentes de Investigación

Un sistema inteligente de investigación que utiliza múltiples agentes especializados para realizar investigaciones estructuradas y detalladas.

## 🚀 Características

- **Arquitectura Multi-Agente**: Sistema coordinado con agentes especializados
- **Workflow Inteligente**: Flujo de trabajo estructurado con LangGraph
- **Integración OpenAI**: Uso de GPT-4 para análisis y generación de contenido
- **Validación Humana**: Interfaz para aprobación de esquemas de investigación
- **Investigación Estructurada**: Generación automática de esquemas y reportes detallados

## 📁 Estructura del Proyecto

```
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias del proyecto
├── research_agent/                  # Paquete principal
│   ├── __init__.py
│   ├── config/                      # Configuración
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/                      # Modelos de datos
│   │   ├── __init__.py
│   │   └── state.py
│   ├── agents/                      # Agentes especializados
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── supervisor.py
│   │   └── investigator.py
│   ├── tools/                       # Herramientas
│   │   ├── __init__.py
│   │   └── openai_client.py
│   └── workflows/                   # Workflows
│       ├── __init__.py
│       └── research_workflow.py
└── research_agent_basic.py          # Versión básica (legacy)
```

## 🛠️ Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd Challenge_WL
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="tu-api-key-aqui"
   ```

## 🎯 Uso

### Ejecución Básica

```bash
python main.py
```

### Uso Programático

```python
from research_agent.workflows.research_workflow import ResearchWorkflow

# Crear workflow
workflow = ResearchWorkflow()

# Ejecutar investigación
result = workflow.run("Investigá las tendencias actuales en IA aplicada a medicina")
```

## 🔧 Componentes del Sistema

### 1. Agente Supervisor
- Coordina el flujo de trabajo
- Decide qué acción tomar en cada paso
- Gestiona la transición entre agentes

### 2. Agente Investigador
- Genera esquemas de investigación estructurados
- Realiza investigaciones detalladas usando OpenAI
- Proporciona análisis y reportes completos

### 3. Workflow de Investigación
- Define el flujo de trabajo con LangGraph
- Maneja la validación humana
- Coordina la comunicación entre agentes

## 🔄 Flujo de Trabajo

1. **Inicio**: El supervisor recibe la consulta del usuario
2. **Generación de Esquema**: El investigador crea un esquema estructurado
3. **Validación Humana**: El usuario aprueba o modifica el esquema
4. **Investigación Detallada**: El investigador realiza la investigación completa
5. **Finalización**: Se genera el reporte final

## 📊 Ejemplo de Salida

```
🚀 SISTEMA DE AGENTES DE INVESTIGACIÓN
============================================================

📋 CONSULTA: Investigá las tendencias actuales en inteligencia artificial aplicada a medicina
============================================================

🤖 SUPERVISOR: Iniciando proceso de investigación
🤖 INVESTIGADOR: Analizando consulta: 'Investigá las tendencias actuales en inteligencia artificial aplicada a medicina'
🤖 INVESTIGADOR: Generando esquema de investigación...
🤖 INVESTIGADOR: ✅ Esquema de investigación generado

============================================================
🤝 VALIDACIÓN HUMANA REQUERIDA
============================================================

📋 ESQUEMA DE INVESTIGACIÓN PROPUESTO:
## ESQUEMA DE INVESTIGACIÓN

### 1. Fundamentos de IA en Medicina
- Definiciones y conceptos clave
- Tipos de IA aplicada a la salud
- Fuentes: Literatura médica, papers académicos
- Preguntas clave: ¿Qué tipos de IA se usan en medicina?

### 2. Aplicaciones Actuales
- Diagnóstico por imágenes
- Análisis de datos médicos
- Medicina personalizada
- Fuentes: Casos de estudio, implementaciones reales
- Preguntas clave: ¿Cuáles son los casos de éxito actuales?

[...]

Tu decisión [s/n/q]: s
✅ Esquema aprobado, continuando con investigación...

🤖 SUPERVISOR: Esquema aprobado, iniciando investigación detallada
🤖 INVESTIGADOR: Realizando investigación detallada...
🤖 INVESTIGADOR: ✅ Investigación detallada completada

============================================================
📊 RESULTADOS FINALES
============================================================

📋 Consulta original: Investigá las tendencias actuales en inteligencia artificial aplicada a medicina

🔍 Investigación completada:
[Reporte detallado con toda la información investigada]

📈 Pasos ejecutados: 4
✅ Estado final: Supervisor
```

## 🔧 Configuración

### Variables de Entorno

- `OPENAI_API_KEY`: Tu clave de API de OpenAI (requerida)
- `OPENAI_MODEL`: Modelo a usar (default: "gpt-4")

### Configuración de Agentes

- `MAX_RETRIES`: Número máximo de reintentos (default: 3)
- `TIMEOUT`: Timeout para operaciones (default: 30 segundos)

## 🚀 Próximos Pasos

- [ ] Integración con APIs de búsqueda web (Google, Bing)
- [ ] Agentes especializados por dominio
- [ ] Interfaz web para validación humana
- [ ] Almacenamiento de resultados en base de datos
- [ ] Sistema de plugins para herramientas adicionales

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias y mejoras. 