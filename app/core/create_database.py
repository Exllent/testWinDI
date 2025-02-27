import asyncio

from app.core.database import engine
from app.models import Message, Group, Chat
from app.models.user_model import User, Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
