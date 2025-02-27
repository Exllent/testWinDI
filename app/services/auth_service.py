from datetime import datetime, timedelta
# from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_config
from app.repositories import UserRepository

from app.models import User
from sqlalchemy.future import select

from app.schemas import LoginRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # @staticmethod
    # def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    #     to_encode = data.copy()
    #     expire = datetime.utcnow() + (expires_delta or auth_config.access_token_expire)
    #     to_encode.update({"exp": expire})
    #     return jwt.encode(to_encode, auth_config.secret_key, algorithm=auth_config.algorithm)

    @staticmethod
    async def authenticate_user(db: AsyncSession, user: LoginRequest) -> dict | None:
        db_user: User = await UserRepository(session=db).get_by_data({"email": user.email})
        if db_user and AuthService.verify_password(user.password, db_user.password):
            return {"access_token": "aaa"}
        raise Exception
