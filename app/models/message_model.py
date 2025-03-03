from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

from app.core import Base


class Message(Base):
    __tablename__ = "messages"

    id: int = Column(Integer, primary_key=True, index=True)
    chat_id: int = Column(ForeignKey("chats.id"))
    sender_id: int = Column(ForeignKey("users.id"))
    text: str = Column(String, nullable=False)
    timestamp: datetime = Column(DateTime(timezone=True), default=datetime.now(tz=timezone.utc))
    is_read: bool = Column(Boolean, default=False)


class MessageReadStatus(Base):
    __tablename__ = "message_read_status"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    has_read = Column(Boolean, default=False)
