from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.core import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("chat_id", "user_id", name='uniq_chat_user'),)
