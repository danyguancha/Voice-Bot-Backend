
from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response, devuelve_nivel_felicidad
from controllers.audioController import listen_and_transcribe
from helper.filters import GREETINGS, FAREWELLS, FINANCIAL_TERMS
from helper.lectorData import get_users
import markdown
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


def get_bot_response(message: chat_schemas.MessageCreate, db):
    

    bot_response = generate_response(message.text)
    #SE AGREGO USER EMOTION PARA QUE SE PUEDA VISUALIZAR EN EL FRONTEND
    user_emotion = devuelve_nivel_felicidad(message.text)
    bot_emotion = "Neutral"    
    bot_response_html = markdown.markdown(bot_response)
    
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
    

    bot_emotion = "Neutral"    
    
    # Guardar el mensaje en la base de datos
    db_message = Message(text=message.text, user_emotion = user_emotion, bot_emotion = bot_emotion, response=bot_response_html)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    response_data = {
        "response": bot_response_html,
        "token_count": token_count,
        "cost": cost,
        "word_count": word_count,
        "user_emotion": user_emotion
    }

    print("Debugging Response Data:", response_data)

    return response_data




# Función para verificar si el mensaje es un saludo
def is_greeting(text: str) -> bool:
    text = text.lower()  # Convertir el texto a minúsculas
    return any(greeting in text for greeting in GREETINGS)

# Función para verificar si el mensaje es una despedida
def is_farewell(text: str) -> bool:
    text = text.lower()  # Convertir el texto a minúsculas
    return any(farewell in text for farewell in FAREWELLS)

# Función para verificar si el mensaje está relacionado con administración financiera
def is_financial_topic(text: str) -> bool:
    text = text.lower()  # Convertir el texto a minúsculas
    return any(term in text for term in FINANCIAL_TERMS)

def get_input(db):
    # Obtener el ultimo texto de entrada por parte del usuario
    last_message = db.query(Message).order_by(Message.id.desc()).first()
    if last_message:
        return last_message.text
    return None

def get_initial_bot_message(numero_documento, db):
    nombre, monto = consult_debtor(numero_documento)

    initial_message = f"¡Hola! {nombre}, un gusto sa"
    bot_response_html = markdown.markdown(initial_message)
    
    # Guardar el mensaje inicial en la base de datos
    db_message = Message(text=None, response=bot_response_html)  # No hay texto de usuario aún
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return {"response": bot_response_html}


def consult_debtor(numero_documento):
    user_debtor = consult_user(numero_documento)
    nombre = ''
    monto = 0
    if user_debtor:
        nombre = user_debtor['Nombre_Cliente']
        monto = user_debtor['Monto_Deuda']
    return nombre, monto
        
def consult_user(numero_documento):
    users = get_users()
    for user in users:
        if user['Numero_Documento'] == numero_documento:
            return user
    

    
    