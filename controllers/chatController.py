from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response
from controllers.audioController import listen_and_transcribe
from helper.filters import GREETINGS, FAREWELLS, FINANCIAL_TERMS
import markdown
import nltk
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
from models.tables import Message
import markdown
import re

# Configurar y verificar la descarga del recurso punkt
nltk.data.path.append("C:\\nltk_data")  # Ruta personalizada para nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir="C:\\nltk_data")

def get_bot_response(message, db):
    # Obtener el último mensaje para contextualizar la respuesta
    last_message = get_input(db)

    # Verificar si el mensaje es un saludo o despedida
    if is_greeting(message.text):
        bot_response = "¡Hola! ¿En qué puedo ayudarte hoy?"
    elif is_farewell(message.text):
        bot_response = "¡Hasta luego! Que tengas un buen día."
    elif not is_financial_topic(message.text):
        bot_response = "Lo siento, no puedo responder preguntas fuera del ámbito de la administración financiera."
    else:
        context_prompt = f"Última pregunta: {last_message}. Ahora la nueva pregunta es: {message.text}"
        bot_response = generate_response(context_prompt)

    # Procesar la respuesta generada
    bot_response_html = markdown.markdown(bot_response)

    # Limpiar texto de etiquetas HTML
    clean_text = BeautifulSoup(bot_response_html, "html.parser").get_text()

    # Tokenización alternativa si nltk falla
    try:
        words = word_tokenize(clean_text)
    except LookupError:
        # Si nltk no funciona, usar regex como alternativa
        words = re.findall(r'\b\w+\b', clean_text)

    # Calcular palabras y tokens
    word_count = len(words)
    token_count = word_count  # En este caso, 1 token = 1 palabra
    cost = token_count * 0.25  # Ajustar el costo si aplica

    # Guardar el mensaje en la base de datos
    db_message = Message(text=message.text, response=bot_response_html)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    response_data = {
        "response": bot_response_html,
        "token_count": token_count,
        "cost": cost,
        "word_count": word_count
    }

    print("Debugging Response Data:", response_data)

    return response_data

# Función para verificar si el mensaje es un saludo
def is_greeting(text: str) -> bool:
    text = text.lower()
    return any(greeting in text for greeting in GREETINGS)

# Función para verificar si el mensaje es una despedida
def is_farewell(text: str) -> bool:
    text = text.lower()
    return any(farewell in text for farewell in FAREWELLS)

# Función para verificar si el mensaje está relacionado con administración financiera
def is_financial_topic(text: str) -> bool:
    text = text.lower()
    return any(term in text for term in FINANCIAL_TERMS)

def get_input(db):
    # Obtener el último texto de entrada por parte del usuario
    last_message = db.query(Message).order_by(Message.id.desc()).first()
    if last_message:
        return last_message.text
    return None
