from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import UserAlreadyExistsException
from app.models import User
from app.repositories import UserRepository
from app.schemas.user_schema import UserCreate


class UserService:

    def __init__(self, db: AsyncSession):
        self.session = db

    async def register_user(self, user: UserCreate, hasher: Callable[[str], str]) -> int:
        hashed_password = hasher(user.password)
        user_data = user.model_dump()
        user_data['password'] = hashed_password
        result = await UserRepository(session=self.session).create_one(user_data)
        if result is None:
            raise UserAlreadyExistsException(message=f"User with email {user.email} already exists")
        return result

    async def get_user(self, user_id: int) -> Optional[User]:
        return await UserRepository(session=self.session).get_by_data({"id": user_id})
