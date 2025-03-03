import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, CheckConstraint, UniqueConstraint

from app.core import Base


class ChatTypeEnum(str, enum.Enum):
    personal = "personal"
    group = "group"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(ChatTypeEnum), nullable=False)
    owner_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        CheckConstraint('owner_id <> recipient_id', name='check_owner_not_recipient'),
        UniqueConstraint("owner_id", "recipient_id", name="unq_owner_recipient")
    )
