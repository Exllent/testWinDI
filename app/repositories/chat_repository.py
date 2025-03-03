from sqlalchemy import select, column, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SQLAlchemyRepository
from app.models import Chat, Group


class ChatRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, model=Chat)

    async def get_type_with_user_auth(self, chat_id: int, user_id: int):
        stmt = (
            select(Chat.type)
            .where(
                (Chat.id == chat_id) & ((Chat.owner_id == user_id) | (Chat.recipient_id == user_id)) |
                select(exists(Group)).where((Group.chat_id == chat_id) & (Group.user_id == user_id))
            )
        )
        result = await self.session.execute(stmt)
        return result.first()
