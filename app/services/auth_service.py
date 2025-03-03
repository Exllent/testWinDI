from datetime import timedelta, datetime, timezone
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import jwt

from app.core import auth_config
from app.repositories import UserRepository
from app.exceptions import InvalidCredentials
from app.models import User
from app.schemas import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    def __init__(self, db: AsyncSession):
        self.session = db

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + (expires_delta or auth_config.access_token_expire)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, auth_config.secret_key, algorithm=auth_config.algorithm)

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> Token:
        db_user: User = await UserRepository(session=self.session).get_by_data({"email": form_data.username})
        if db_user and AuthService.verify_password(form_data.password, db_user.password):
            access_token = self.create_access_token({"uid": db_user.id}, auth_config.access_token_expire)
            return Token(access_token=access_token, token_type="bearer")
        raise InvalidCredentials(message="Invalid credentials")
