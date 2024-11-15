from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response
from controllers.audioController import listen_and_transcribe
from helper.filters import GREETINGS, FAREWELLS, FINANCIAL_TERMS
from helper.lectorData import get_users
import markdown


def get_bot_response(message: chat_schemas.MessageCreate, db):
    

    bot_response = generate_response(message.text)
    user_emotion = 0.0
    bot_emotion = "Neutral"    
    bot_response_html = markdown.markdown(bot_response)
    
    # Guardar el mensaje en la base de datos
    db_message = Message(text=message.text, user_emotion = user_emotion, bot_emotion = bot_emotion, response=bot_response_html)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return {"response": bot_response_html}




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
    

    
    
