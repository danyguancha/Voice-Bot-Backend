from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response
from controllers.audioController import listen_and_transcribe
from helper.filters import GREETINGS, FAREWELLS, FINANCIAL_TERMS
import markdown


def get_bot_response(message: chat_schemas.MessageCreate, db):
    # Obtener el último mensaje para contextualizar la respuesta
    last_message = get_input(db)
    
    # Verificar si el mensaje es un saludo o despedida
    if is_greeting(message.text):
        bot_response = "¡Hola! ¿En qué puedo ayudarte hoy?"
    elif is_farewell(message.text):
        bot_response = "¡Hasta luego! Que tengas un buen día."
    # Verificar si el mensaje está relacionado con administración financiera
    elif not is_financial_topic(message.text):
        bot_response = "Lo siento, no puedo responder preguntas fuera del ámbito de la administración financiera."
    else:
        # Generar una respuesta que tome en cuenta el contexto
        context_prompt = f"Última pregunta: {last_message}. Ahora la nueva pregunta es: {message.text}"
        bot_response = generate_response(context_prompt)
        
    bot_response_html = markdown.markdown(bot_response)
    
    # Guardar el mensaje en la base de datos
    db_message = Message(text=message.text, response=bot_response_html)
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
