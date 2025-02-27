from fastapi import APIRouter

from app.api.v1 import user_router, auth_router, ws_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router, prefix="/users", tags=["Users"])
auth_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(ws_router, tags=["Chats"])
