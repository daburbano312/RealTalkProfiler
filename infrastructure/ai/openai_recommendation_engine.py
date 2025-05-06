# infrastructure/ai/openai_recommendation_engine.py
import httpx
from openai import OpenAI
import json # Importar json
from core.utils.db_utils import obtener_proyectos_inmobiliarios

# Desactivar la verificación SSL (solo para desarrollo, considera alternativas seguras en producción)
# OpenAI.verify_ssl_certs = False # Comentado o eliminado si ya no es necesario

class OpenAIRecommendationEngine:
    def __init__(self, api_key):
        # Considera manejar la verificación SSL de forma más segura si es posible
        self.client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))

    def generate_advice(self, emotion, keywords, transcript):
        """
        Genera un ranking de proyectos sugeridos basado en el perfil del cliente
        y devuelve la respuesta parseada como un diccionario Python.
        """
        proyectos_info = obtener_proyectos_inmobiliarios()
        prompt = f"""
Eres un asesor experto en ventas inmobiliarias. Basado en el siguiente perfil de cliente:

Emoción predominante: {emotion}
Palabras clave detectadas: {', '.join(keywords)}
Transcripción de lo que dijo el cliente: "{transcript}"

Proyectos inmobiliarios disponibles:
{proyectos_info}

Analiza los proyectos disponibles y el perfil del cliente. Identifica los 3 proyectos más adecuados para este cliente.
Devuelve tu respuesta ÚNICAMENTE en formato JSON de la siguiente manera:
{{
  "suggested_projects": [
    {{ "project_id": <ID_PROYECTO_INT>, "name": "<NOMBRE_PROYECTO>", "reason": "<BREVE_JUSTIFICACIÓN_POR_QUÉ_ES_ADECUADO>", "score": <PUNTAJE_NUMERICO_1_A_10> }},
    {{ "project_id": <ID_PROYECTO_INT>, "name": "<NOMBRE_PROYECTO>", "reason": "<BREVE_JUSTIFICACIÓN>", "score": <PUNTAJE_NUMERICO_1_A_10> }},
    {{ "project_id": <ID_PROYECTO_INT>, "name": "<NOMBRE_PROYECTO>", "reason": "<BREVE_JUSTIFICACIÓN>", "score": <PUNTAJE_NUMERICO_1_A_10> }}
  ]
}}
Sé conciso y enfócate en la relevancia para el cliente. Solo devuelve el JSON válido. Asegúrate que los IDs y scores sean números.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4", # O el modelo que estés usando
                messages=[
                    {"role": "system", "content": "Asistente de ventas inmobiliarias experto en análisis de proyectos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5, # Ajusta según necesidad
                max_tokens=300 # Aumenta si el JSON es largo
            )

            content = response.choices[0].message.content.strip()

            # Intentar parsear la respuesta JSON
            try:
                # A veces GPT envuelve el JSON en ```json ... ```, intentamos limpiarlo
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                ranked_suggestions = json.loads(content)
                # Validar estructura básica
                if isinstance(ranked_suggestions, dict) and "suggested_projects" in ranked_suggestions and isinstance(ranked_suggestions["suggested_projects"], list):
                     print(f"✅ Ranking JSON parseado correctamente: {ranked_suggestions}")
                     return ranked_suggestions
                else:
                    print(f"⚠️ JSON recibido no tiene la estructura esperada: {content}")
                    return {"error": "Formato de ranking inesperado", "raw": content}

            except json.JSONDecodeError as json_err:
                print(f"❌ Error al parsear JSON de OpenAI: {json_err}")
                print(f"Respuesta recibida: {content}")
                return {"error": "Respuesta de IA no es JSON válido", "raw": content}

        except Exception as e:
            print(f"❌ Error durante la llamada a OpenAI: {e}")
            # Devolver un diccionario de error consistente
            return {"error": f"Error en API de OpenAI: {str(e)}", "raw": ""}