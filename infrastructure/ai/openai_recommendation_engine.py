import httpx
from openai import OpenAI
# Desactivar la verificación SSL (solo para desarrollo)
OpenAI.verify_ssl_certs = False
from core.utils.db_utils import obtener_proyectos_inmobiliarios



class OpenAIRecommendationEngine:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))

    def generate_advice(self, emotion, keywords, transcript):

        proyectos_info = obtener_proyectos_inmobiliarios()
        prompt = f"""
Eres un asesor experto en ventas inmobiliarias. Basado en el siguiente perfil de cliente:

Emoción predominante: {emotion}
Palabras clave detectadas: {', '.join(keywords)}
Transcripción de lo que dijo el cliente: "{transcript}"
Información de proyectos inmobiliarios disponibles:{proyectos_info}
Genera una recomendación clara y empática para ayudar al asesor a responder mejor a este cliente.
La respuesta debe ser en español y directa.
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Asistente de ventas inmobiliarias."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()
