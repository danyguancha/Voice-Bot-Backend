
from models.tables import Message
from schemas import chat as chat_schemas
from config.configurationIA import generate_response, devuelve_nivel_felicidad
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
    #SE AGREGO USER EMOTION PARA QUE SE PUEDA VISUALIZAR EN EL FRONTEND
    user_emotion = devuelve_nivel_felicidad(message.text)
    bot_emotion = "Neutral"    
    bot_response_html = markdown.markdown(bot_response)

    # Limpiar el texto de etiquetas HTML
    clean_text = BeautifulSoup(bot_response_html, "html.parser").get_text()

    # Calcular métricas
    texto = str(clean_text)
    cantidad_palabras = len(texto.split())
    numero_de_tokens = contar_tokens(texto)
    costo = calcular_costo(numero_de_tokens)

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
        "token_count": numero_de_tokens,
        "cost": costo,
        "word_count": cantidad_palabras
    }

    # Actualizar acumulador con los datos actuales,
        "user_emotion": user_emotion
    response_accumulator.update(response_data)
    print("valor acumulado todos los datos ",response_accumulator)
    print("valor acumulado todos los datos de toda la response data ",response_data)
    # Retornar datos actuales y acumulados    return {
        "current_response": response_data,
        "accumulated_totals": response_accumulator.get_totals()
    }




# Obtener el último mensaje de la base de datos
def get_input(db):
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
    if user_debtor:
        name = user_debtor['Nombre_Cliente']



        
def consult_user(numero_documento):
    users = get_users()
    for user in users:
        if user['Numero_Documento'] == numero_documento:
            return user
    

    
    
