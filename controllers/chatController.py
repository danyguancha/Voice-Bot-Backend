from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response
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
    """
    Maneja el flujo del chatbot, comenzando por capturar el número de documento como una cadena.
    """
    # Obtener el último mensaje del usuario
    last_input = get_input(db)

    if not last_input:
        # Si no hay un mensaje previo, envía el mensaje inicial
        return get_first_bot_message(db)

    # Validar el número de documento
    if last_input:
        numero_documento = message.text.replace(" ", "")
        if numero_documento:
            # Mensaje con la información del documento
            return get_second_bot_message(numero_documento, db)
        else:
            # Solicitar nuevamente un número de documento válido
            error_message = "Por favor, proporcióname un número de documento válido."
            return {"response": markdown.markdown(error_message)}

    # Flujo después de capturar el número de documento
    bot_response = generate_response(message.text)
    emotion = "Neutral"
    bot_response_html = markdown.markdown(bot_response)

    # Limpiar el texto de etiquetas HTML
    clean_text = BeautifulSoup(bot_response_html, "html.parser").get_text()

    # Tokenización y conteo de palabras
    words = word_tokenize(clean_text)
    word_count = len(words)
    token_count = word_count
    cost = token_count * 0.25

    # Guardar el mensaje en la base de datos
    db_message = Message(
        text=message.text,
        user_emotion=emotion,
        bot_emotion=emotion,
        response=bot_response_html
    )
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



def get_input(db):
    # Obtener el ultimo texto de entrada por parte del usuario
    last_message = db.query(Message).order_by(Message.id.desc()).first()
    #last_message = db.query(Message).filter(Message.text.isnot(None)).order_by(Message.id.desc()).first()
    if last_message:
        return last_message.text
    return None

def is_number(text: str) -> bool:
    # Verificar si el texto es un número válido
    return re.match(r'^\d+$', text) is not None

def get_second_bot_message(numero_documento, db):
    # Generar el mensaje basado en el número de documento
    nombre, monto = consult_debtor(numero_documento)
    if not nombre:
        error_message = f"No encontramos información asociada al documento {numero_documento}. Por favor, verifica el número."
        return {"response": markdown.markdown(error_message)}

    initial_message = (
        f"¡Hola, {nombre}! Un gusto saludarlo. "
        f"Le habla la asistente virtual de Indra. "
        f"Lo estoy contactando para que podamos conversar sobre el vencimiento de su factura por un monto de {monto} pesos colombianos."
    )
    bot_response_html = markdown.markdown(initial_message)
    
    # Guardar el mensaje en la base de datos
    db_message = Message(text=initial_message, user_emotion = 0.0, bot_emotion='Neutral', response=bot_response_html)  # No hay texto del usuario aún
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return {"response": bot_response_html}

def get_first_bot_message(db):
    # Mensaje inicial del bot
    initial_message = "¡Hola! Soy la asistente virtual de Indra. Me puedes proporcionar tu número de documento para poder ayudarte con tu consulta."
    bot_response_html = markdown.markdown(initial_message)
    userEmotion = 0.0
    botEmotion = "Neutral"
    # Guardar el mensaje inicial en la base de datos
    db_message = Message(text=initial_message, user_emotion=userEmotion, bot_emotion=botEmotion, response=bot_response_html)  # No hay texto del usuario aún
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
    

    
    