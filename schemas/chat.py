from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    text: str
    #MODIFIQUE ESTA PARTE PARA QUE PUEDA LEER
    #user_emotion: float
    #bot_emotion: str

class MessageResponse(BaseModel):
    id: int
    text: str
    response: str
    created_at: datetime
    

