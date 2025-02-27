from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_id(self, obj_id: int) -> User | None:
        return await super().get_by_id(obj_id=obj_id)
