
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from config.db import get_db
from controllers.audioController import listen_and_transcribe, text_to_speech
from controllers.chatController import get_bot_response, get_input, get_second_bot_message
from schemas import chat as chat_schemas
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

@router.post("/chat/")
async def chat(audio: UploadFile = File(...), db: Session = Depends(get_db)):
    # Lee el contenido del archivo de audio
    audio_bytes = await audio.read()

    # Convierte el audio en un archivo en memoria para procesarlo
    audio_file = io.BytesIO(audio_bytes)

    # Transcribe el audio
    transcription = listen_and_transcribe(audio_file)
    if transcription is None:
        raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")

    # Obtener respuesta del bot
    message_data = chat_schemas.MessageCreate(text=transcription)
    bot_response = get_bot_response(message_data, db)

    return {
        "response": bot_response["response"],
        "text": transcription,
        "num_token_count": bot_response["num_token_count"],
        "cost": bot_response["cost"],
        "word_count": bot_response["word_count"],
        "user_emotion": bot_response["user_emotion"],
        "accumulated_totals": bot_response["accumulated_totals"]
    }

@router.get("/chat_first_message/")
async def get_first_message(db: Session = Depends(get_db)):
    first_message = get_second_bot_message(db)
    return first_message

@router.get("/input_text/")
async def get_last_input(db: Session = Depends(get_db)):

    input_text = get_input(db)
    if input_text is None:
        raise HTTPException(status_code=404, detail="No hay mensajes de entrada en la base de datos")
    return {"text": input_text}

