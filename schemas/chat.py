from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    text: str
    user_emotion: Optional[float] = None
    bot_emotion: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    text: str
    response: str
    created_at: datetime

