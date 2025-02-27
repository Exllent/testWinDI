from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.repositories import UserRepository
from app.schemas.user_schema import UserCreate
from app.exceptions import UserAlreadyExistsException
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(self, password: str) -> bool:
    return pwd_context.verify(password, self.password_hash)


class UserService:
    @staticmethod
    async def register_user(db: AsyncSession, user: UserCreate) -> int:
        hashed_password = pwd_context.hash(user.password)
        user_data = user.model_dump()
        user_data['password'] = hashed_password

        result = await UserRepository(session=db).create_one(user_data)
        if result is None:
            raise UserAlreadyExistsException(message=f"User with email {user.email} already exists")
        return result

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        return await UserRepository(session=db).get_by_id(user_id)
