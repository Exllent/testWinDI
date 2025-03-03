from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)
