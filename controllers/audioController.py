import speech_recognition as sr
from pydub import AudioSegment
import io
from gtts import gTTS
from bs4 import BeautifulSoup

def listen_and_transcribe(audio_file):
    recognizer = sr.Recognizer()
    
    # Convierte el audio a WAV usando pydub
    try:
        audio_segment = AudioSegment.from_file(audio_file)
        audio_wav = io.BytesIO()
        audio_segment.export(audio_wav, format="wav")
        audio_wav.seek(0)
    except Exception as e:
        print(f"Error al convertir el audio: {e}")
        return None

    # Procesa el archivo de audio en formato WAV
    with sr.AudioFile(audio_wav) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="es-ES")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Error al solicitar resultados a Google Speech Recognition: {e}")
        return None
    
def text_to_speech(text: str):
    # Eliminar las etiquetas HTML utilizando BeautifulSoup
    clean_text = BeautifulSoup(text, "html.parser").get_text()
    
    # Generar el archivo de audio con el texto limpio
    tts = gTTS(clean_text, lang="es")
    audio_path = "static/response_audio.mp3"
    tts.save(audio_path)
    
    return audio_path  
