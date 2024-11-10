import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env')
key_api = os.getenv('API_KEY')

# Configurar la API de Google Generative AI
genai.configure(api_key=key_api)

# Función para generar contenido usando el modelo
def generate_response(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
