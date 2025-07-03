"""
Cliente para interactuar con OpenAI
"""
from openai import OpenAI
from research_agent.config.settings import Settings

class OpenAIClient:
    """Cliente para OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.OPENAI_MODEL
    
    def generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        """Genera respuesta usando OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un investigador experto especializado en análisis detallados y estructurados."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error en OpenAI API: {e}") 