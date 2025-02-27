from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core import db_config, db_setting

engine = create_async_engine(db_config.postgres_url, echo=db_setting.echo)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=db_setting.expire_on_commit)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



