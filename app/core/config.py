from dataclasses import dataclass
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "password")
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", 5432))
    db: str = os.getenv("POSTGRES_DB", "mydatabase")

    @property
    def postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass(frozen=True)
class DatabaseSettings:
    echo: bool = os.getenv("DB_ECHO", "False").lower() in ("true", "1")
    expire_on_commit: bool = os.getenv("DB_EXPIRE_ON_COMMIT", "False").lower() in ("true", "1")


@dataclass(frozen=True)
class OAuthConfig:
    secret_key: str = os.getenv("SECRET_KEY", "")
    refresh_key: str = os.getenv("REFRESH_SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire: timedelta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE", 5)))
    refresh_token_expire: timedelta = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE", 1)))


db_config = DatabaseConfig()
db_setting = DatabaseSettings()
auth_config = OAuthConfig()
