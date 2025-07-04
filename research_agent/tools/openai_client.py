"""
Cliente para interactuar con OpenAI con optimización de costos
"""
from openai import OpenAI
from research_agent.config.settings import Settings
from research_agent.tools.cost_optimizer import CostOptimizer

class OpenAIClient:
    """Cliente para OpenAI API con optimización inteligente de costos"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.fallback_model = Settings.OPENAI_MODEL
    
    def generate_response(self, prompt: str, task_type: str = "general", 
                         max_tokens: int = 2000, system_prompt: str = None) -> str:
        """
        Genera respuesta usando el modelo óptimo basado en la complejidad de la tarea
        
        Args:
            prompt: Prompt del usuario
            task_type: Tipo de tarea para optimización (outline, research, analysis, report)
            max_tokens: Máximo de tokens
            system_prompt: Prompt del sistema personalizado
            
        Returns:
            Respuesta generada
        """
        # Seleccionar modelo óptimo basado en complejidad
        optimal_model = CostOptimizer.get_optimal_model(task_type, len(prompt))
        
        # System prompt por defecto o personalizado
        if system_prompt is None:
            system_prompt = self._get_system_prompt_for_task(task_type)
        
        try:
            print(f"💡 Usando modelo {optimal_model} para tarea: {task_type}")
            
            response = self.client.chat.completions.create(
                model=optimal_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self._get_temperature_for_task(task_type)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Error con modelo {optimal_model}, usando fallback {self.fallback_model}")
            # Fallback al modelo por defecto
            try:
                response = self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as fallback_error:
                raise Exception(f"Error en OpenAI API: {fallback_error}")
    
    def _get_system_prompt_for_task(self, task_type: str) -> str:
        """Retorna el system prompt apropiado para cada tipo de tarea"""
        prompts = {
            "outline": "Eres un experto en estructuración de información que crea esquemas de investigación claros y organizados.",
            "research": "Eres un investigador especializado que encuentra y sintetiza información relevante y actualizada.",
            "analysis": "Eres un analista experto que examina información en profundidad y extrae insights valiosos.",
            "curation": "Eres un curador de contenido que organiza y sintetiza información de múltiples fuentes.",
            "report": "Eres un escritor técnico experto que crea reportes estructurados, claros y profesionales.",
            "general": "Eres un asistente experto especializado en análisis detallados y estructurados."
        }
        return prompts.get(task_type, prompts["general"])
    
    def _get_temperature_for_task(self, task_type: str) -> float:
        """Retorna la temperatura apropiada para cada tipo de tarea"""
        temperatures = {
            "outline": 0.3,      # Más determinístico para estructura
            "research": 0.5,     # Balance para investigación
            "analysis": 0.4,     # Ligeramente creativo para insights
            "curation": 0.4,     # Balance para síntesis
            "report": 0.6,       # Más creativo para escritura
            "general": 0.7       # Default
        }
        return temperatures.get(task_type, 0.7) 