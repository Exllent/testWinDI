from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi_pagination import add_pagination
from app.api import auth_router, ws_router, user_router, chat_router, message_router
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
add_pagination(app)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat_router, prefix="/chats", tags=["Chats"])
api_router.include_router(message_router, prefix="/messages", tags=["Messages"])
api_router.include_router(ws_router)

app.include_router(api_router)
