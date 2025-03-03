"""some"""

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi_pagination import add_pagination
from app.api import auth_router, ws_router, user_router, chat_router, message_router

app = FastAPI()
add_pagination(app)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat_router, prefix="/chats", tags=["Chats"])
api_router.include_router(message_router, prefix="/messages", tags=["Messages"])
api_router.include_router(ws_router, tags=["WS"])

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
