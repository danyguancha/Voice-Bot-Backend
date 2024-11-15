from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response
from controllers.audioController import listen_and_transcribe
from helper.filters import GREETINGS, FAREWELLS, FINANCIAL_TERMS
from helper.lectorData import get_users
import markdown
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import nltk

nltk.download('punkt')  # Descargar recursos necesarios para tokenización

# Clase acumuladora
class Accumulator:
    def __init__(self):
        self.data = {
            "token_count": 0,
            "cost": 0.0,
            "word_count": 0
        }

    def update(self, response_data):
        self.data["token_count"] += response_data.get("token_count", 0)
        self.data["cost"] += response_data.get("cost", 0.0)
        self.data["word_count"] += response_data.get("word_count", 0)

    def get_totals(self):
        return self.data


# Instancia de acumulador global
response_accumulator = Accumulator()


# Función para contar tokens
def contar_tokens(texto):
    tokens = word_tokenize(texto)
    return len(tokens)


# Función para calcular costo
def calcular_costo(numero_de_tokens, costo_por_1000_tokens=0.00001875):
    costo_total = (numero_de_tokens / 1000) * costo_por_1000_tokens
    return costo_total


def get_bot_response(message: chat_schemas.MessageCreate, db):
    # Obtener el último mensaje para contextualizar la respuesta
    last_message = get_input(db)

    # Generar una respuesta que tome en cuenta el contexto
    context_prompt = f"Última pregunta: {last_message}. Ahora la nueva pregunta es: {message.text}"
    bot_response = generate_response(message.text)

    # Procesar la respuesta generada
    bot_response_html = markdown.markdown(bot_response)

    # Limpiar texto de etiquetas HTML
    clean_text = BeautifulSoup(bot_response_html, "html.parser").get_text()

    # Calcular métricas
    texto = str(clean_text)
    cantidad_palabras = len(texto.split())
    numero_de_tokens = contar_tokens(texto)
    costo = calcular_costo(numero_de_tokens)

    # Guardar el mensaje en la base de datos
    db_message = Message(text=message.text, response=bot_response_html)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Datos de respuesta actual
    response_data = {
        "response": bot_response_html,
        "token_count": numero_de_tokens,
        "cost": costo,
        "word_count": cantidad_palabras
    }

    # Actualizar acumulador con los datos actuales
    response_accumulator.update(response_data)
    print("valor acumulado todos los datos ",response_accumulator)
    print("valor acumulado todos los datos de toda la response data ",response_data)
    # Retornar datos actuales y acumulados
    return {
        "current_response": response_data,
        "accumulated_totals": response_accumulator.get_totals()
    }


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


# Obtener el último mensaje de la base de datos
def get_input(db):
    last_message = db.query(Message).order_by(Message.id.desc()).first()
    if last_message:
        return last_message.text
    return None


# Mensaje inicial del bot
def get_initial_bot_message(db):
    initial_message = "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
    bot_response_html = markdown.markdown(initial_message)

    # Guardar el mensaje inicial en la base de datos
    db_message = Message(text=None, response=bot_response_html)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return {"response": bot_response_html}
