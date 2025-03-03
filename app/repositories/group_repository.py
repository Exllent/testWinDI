from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repository import SQLAlchemyRepository

from app.models import Group


class GroupRepository(SQLAlchemyRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Group)
