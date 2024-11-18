
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import ast
import re


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

#Es una funcion que permite detectar las emociones de un texto
def detect_emotion(text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    emociones=["happy","sad","angry","fearful","disgusted","surprised"]
    emocion_respuesta={''}
    reglas="Devuelve un JSON en el rango de -1 a 1, donde -1 es donde siente menos la emocion y +1 donde siente mas la emocion, por ejemplo si esta triste happy esta cercano a -1, si esta feliz, happy esta cercano a +1,con la siguiente estructura: pregunta_usuario={'happy': RANGO DE 0 A -1, 'sad': RANGO DE 0 A -1, 'angry':RANGO DE 0 A -1, 'fearful': -RANGO DE 0 A -1, 'disgusted': RANGO DE 0 A -1, 'surprised': 0.2}, si no puedes procesarlo solo devuelve un JSON con todo en 0 para el siguiente texto"
    response = model.generate_content(reglas+ text)

    print("Datos de la respuesta: ", response.text)

    # Extraer la parte del inicio del response.text que está en comillas triples
    try:
        # Utiliza una expresión regular para encontrar el texto entre comillas triples y etiquetas ```json
        patron = r'```json(.*?)```'
        coincidencia = re.search(patron, response.text, re.DOTALL)
        if coincidencia:
            json_string = coincidencia.group(1).strip()
            # Convierte la cadena JSON en un diccionario de Python
            datos = json.loads(json_string)
            return datos
        else:
            return None  # O maneja el caso donde no se encuentra JSON


    except Exception as e:
        print(f"Error al extraer el texto: {e}")
        return {'pregunta_usuario': {'happy': 0.0}}
    

#Es una funcion que detecta con que emocion se identifica la respuesta del bot
def detect_emotion_response(text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    emociones=["happy","sad","angry","fearful","disgusted","surprised"]
    reglas="Devuelve un json con el valor de la emocion que se identifica en la respuesta del bot, el atributo se llama emocion, de la lista de emociones: happy, sad, angry, fearful, disgusted, surprised, de no existir ninguna,responde neutral, es es el texto"
    reglas_adicionales='El json es asi '
    response = model.generate_content(reglas+ text)

    # Extraer la parte del inicio del response.text que está en comillas triples
    try:
        # Utiliza una expresión regular para encontrar el texto entre comillas triples y etiquetas ```json
        patron = r'```json(.*?)```'
        coincidencia = re.search(patron, response.text, re.DOTALL)
        if coincidencia:
            json_string = coincidencia.group(1).strip()
            # Convierte la cadena JSON en un diccionario de Python
            datos = json.loads(json_string)
            return datos
        else:
            return {'emocion': 'neutral'}  # O maneja el caso donde no se encuentra JSON


    except Exception as e:
        print(f"Error al extraer el texto: {e}")
        return {"emocion":"neutral"}
    

    #Es una funcion que detecta con que emocion se identifica la respuesta del bot, devuelve un rango entre -1 y 1

def devuelve_nivel_felicidad(text: str) -> float:
    print("Texto a procesar:", text)
    #Le pide el JSON a detect_emotion_response
    emocion=detect_emotion(text)
    #El json tiene la forma {'pregunta_usuario': {'happy': 0.8, 'sad': 0, 'angry': 0, 'fearful': 0, 'disgusted': 0, 'surprised': 0}}, devuelve el valor de happy
    #Es decir, va a pregunta_usuario y luego a happy
    try:
        print(emocion)
        return emocion['happy']
    except KeyError:
        print("Error al consultar")
        return 0.0  # Devuelve 0.0 si no se encuentra la clave 'happy'

