"""
Sistema de optimización de costos para selección inteligente de modelos
"""
from enum import Enum
from typing import Dict, Any
from research_agent.config.settings import Settings

class TaskComplexity(Enum):
    """Niveles de complejidad de tareas"""
    SIMPLE = "simple"
    MEDIUM = "medium" 
    COMPLEX = "complex"

class ModelTier(Enum):
    """Niveles de modelos disponibles"""
    BASIC = "gpt-3.5-turbo"
    STANDARD = "gpt-4o-mini"
    PREMIUM = "gpt-4"

class CostOptimizer:
    """Optimizador inteligente de costos para selección de modelos"""
    
    # Mapeo de complejidad a modelo
    MODEL_MAPPING = {
        TaskComplexity.SIMPLE: ModelTier.BASIC,
        TaskComplexity.MEDIUM: ModelTier.STANDARD,
        TaskComplexity.COMPLEX: ModelTier.PREMIUM
    }
    
    # Costos aproximados por 1K tokens (en USD)
    MODEL_COSTS = {
        ModelTier.BASIC: 0.0015,
        ModelTier.STANDARD: 0.00015,
        ModelTier.PREMIUM: 0.03
    }
    
    @classmethod
    def get_optimal_model(cls, task_type: str, content_length: int = 0) -> str:
        """
        Selecciona el modelo óptimo basado en tipo de tarea y longitud
        
        Args:
            task_type: Tipo de tarea (outline, research, analysis, report)
            content_length: Longitud del contenido a procesar
            
        Returns:
            Nombre del modelo a usar
        """
        complexity = cls._assess_complexity(task_type, content_length)
        model_tier = cls.MODEL_MAPPING[complexity]
        
        return model_tier.value
    
    @classmethod
    def _assess_complexity(cls, task_type: str, content_length: int) -> TaskComplexity:
        """Evalúa la complejidad de una tarea"""
        
        # Tareas simples - modelos básicos
        if task_type in ["outline", "summarize", "extract"]:
            return TaskComplexity.SIMPLE
            
        # Tareas complejas - modelos premium
        elif task_type in ["report", "final_analysis", "synthesis"]:
            return TaskComplexity.COMPLEX
            
        # Tareas medias - considerar longitud del contenido
        elif task_type in ["research", "analysis", "curation"]:
            if content_length > 3000:  # Contenido largo necesita modelo mejor
                return TaskComplexity.COMPLEX
            elif content_length > 1000:
                return TaskComplexity.MEDIUM
            else:
                return TaskComplexity.SIMPLE
                
        # Default para tareas no reconocidas
        return TaskComplexity.MEDIUM
    
    @classmethod
    def estimate_cost(cls, task_type: str, estimated_tokens: int) -> float:
        """
        Estima el costo de una tarea
        
        Args:
            task_type: Tipo de tarea
            estimated_tokens: Tokens estimados
            
        Returns:
            Costo estimado en USD
        """
        model = cls.get_optimal_model(task_type)
        model_tier = ModelTier(model)
        cost_per_1k = cls.MODEL_COSTS[model_tier]
        
        return (estimated_tokens / 1000) * cost_per_1k
    
    @classmethod
    def get_cost_summary(cls) -> Dict[str, Any]:
        """Retorna resumen de costos y modelos disponibles"""
        return {
            "models": {tier.name: tier.value for tier in ModelTier},
            "costs_per_1k_tokens": {tier.name: cost for tier, cost in cls.MODEL_COSTS.items()},
            "complexity_mapping": {comp.name: cls.MODEL_MAPPING[comp].name for comp in TaskComplexity}
        }