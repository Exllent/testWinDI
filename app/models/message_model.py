from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

from app.core import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(ForeignKey("chats.id"))
    sender_id = Column(ForeignKey("users.id"))
    receiver_id = Column(ForeignKey("users.id"), nullable=True)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
