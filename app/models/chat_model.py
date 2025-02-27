import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey

from app.core import Base


class ChatTypeEnum(str, enum.Enum):
    personal = "personal"
    group = "group"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ChatTypeEnum), nullable=False)
    owner_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
