from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response, devuelve_nivel_felicidad
from helper.lectorData import get_users
import markdown
from bs4 import BeautifulSoup
import re

class Accumulator:
    def __init__(self):
        self.data = {
            "token_count": 0,
            "cost": 0.0,
            "word_count": 0
        }
        
    def update(self, response_data):
        # Acumular valores de token_count, cost y word_count
        self.data["token_count"] += response_data.get("token_count", 0)
        self.data["cost"] += response_data.get("cost", 0.0)
        self.data["word_count"] += response_data.get("word_count", 0)

    def get_totals(self):
        return self.data

# Instancia del acumulador global
response_accumulator = Accumulator()

def contar_tokens(texto):
    texto = texto.lower()
    tokens = re.findall(r'\b\w+\b|[.,!?;]', texto)
    return len(tokens)

def contar_palabras(texto):
    texto = re.sub(r'[^\w\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    palabras = texto.split()
    return len(palabras)

def calcular_costo(numero_de_tokens, costo_por_1000_tokens=0.00001875):
    costo_total = (numero_de_tokens / 1000) * costo_por_1000_tokens
    return costo_total

def get_bot_response(message: chat_schemas.MessageCreate, db) -> dict:
    bot_response = generate_response(message.text)
    user_emotion = devuelve_nivel_felicidad(message.text)
    bot_emotion = "Neutral"
    bot_response_html = markdown.markdown(bot_response)

    clean_text = BeautifulSoup(bot_response_html, "html.parser").get_text()

    # Calcular métricas de la respuesta
    texto = str(clean_text)
    cantidad_palabras = contar_palabras(texto)
    numero_de_tokens = contar_tokens(texto)
    costo = calcular_costo(numero_de_tokens)

    # Guardar el mensaje en la base de datos
    db_message = Message(
        text=message.text,
        user_emotion=user_emotion,
        bot_emotion=bot_emotion,
        response=bot_response_html
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Actualizar las métricas globales
    response_data = {
        "response": clean_text,
        "text": message.text,
        "num_token_count": numero_de_tokens,
        "cost": costo,
        "word_count": cantidad_palabras,
        "user_emotion": user_emotion,
        "accumulated_totals": response_accumulator.get_totals()
    }

    response_accumulator.update(response_data)
    return response_data

# Obtener el último mensaje de la base de datos
def get_input(db):
    last_message = db.query(Message).order_by(Message.id.desc()).first()
    if last_message:
        return last_message.text
    return None

def get_second_bot_message(db):
    numero_documento = '1234'
    nombre, monto = consult_debtor(numero_documento)
    if not nombre:
        error_message = f"No encontramos información asociada al documento {numero_documento}. Por favor, verifica el número."
        return {"response": markdown.markdown(error_message)}

    initial_message = (
        f"¡Hola, {nombre}! Un gusto saludarlo. "
        f"Le habla la asistente virtual de Indra. "
        f"Lo estoy contactando para que podamos conversar sobre el vencimiento de su factura por un monto de {monto} pesos colombianos."
    )
    bot_response_html = BeautifulSoup(initial_message, "html.parser").get_text()
    userEmotion = devuelve_nivel_felicidad(initial_message)
    botEmotion = "Neutral"
    
    # Guardar el mensaje en la base de datos
    db_message = Message(text=initial_message, user_emotion=userEmotion, bot_emotion=botEmotion, response=bot_response_html)  # No hay texto del usuario aún
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    texto = str(bot_response_html)
    cantidad_palabras = len(texto.split())
    numero_de_tokens = contar_tokens(texto)
    costo = calcular_costo(numero_de_tokens)

    response_data = {
        "response": bot_response_html,
        "text": initial_message,
        "num_token_count": numero_de_tokens,
        "cost": costo,
        "word_count": cantidad_palabras,
        "user_emotion": userEmotion,
        "accumulated_totals": response_accumulator.get_totals()
    }   

    response_accumulator.update(response_data)
    return response_data

def get_first_bot_message(db):
    # Mensaje inicial del bot
    initial_message = "¡Hola! Soy la asistente virtual de Indra. Me puedes proporcionar tu número de documento para poder ayudarte con tu consulta."
    bot_response_html = BeautifulSoup(initial_message, "html.parser").get_text()
    userEmotion = devuelve_nivel_felicidad(initial_message)
    botEmotion = "Neutral"
    # Guardar el mensaje inicial en la base de datos
    db_message = Message(text=initial_message, user_emotion=userEmotion, bot_emotion=botEmotion, response=bot_response_html)  # No hay texto del usuario aún
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    texto = str(bot_response_html)
    cantidad_palabras = len(texto.split())
    numero_de_tokens = contar_tokens(texto)
    costo = calcular_costo(numero_de_tokens)

    response_data = {
        "response": bot_response_html,
        "text": initial_message,
        "num_token_count": numero_de_tokens,  # Cambiar "token_count" a "token_count"
        "cost": costo,
        "word_count": cantidad_palabras,
        "user_emotion": userEmotion,
        "accumulated_totals": response_accumulator.get_totals()
    }   
    response_accumulator.update(response_data)
    return response_data

def consult_debtor(numero_documento):
    user_debtor = consult_user(numero_documento)
    if user_debtor:
        name = user_debtor['Nombre_Cliente']
        monto = user_debtor['Monto_Deuda']
        return name, monto
    return None, None
        
def consult_user(numero_documento):
    users = get_users()
    for user in users:
        if user['Numero_Documento'] == numero_documento:
            return user
