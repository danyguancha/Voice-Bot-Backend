from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from config.db import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_emotion = Column(Float)
    bot_emotion = Column(String(100))
