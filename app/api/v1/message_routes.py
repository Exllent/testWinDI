from datetime import datetime, timezone

from asyncio import create_task
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, Params

from app.core import get_current_user_id, get_db
from app.schemas import MessageResponse
from app.services import MessageService
from app.ws_manager import WebSocketManager
from app.exceptions import (
    InternalServerErrorException,
    MessageNotFoundException,
    MessageAlreadyReadException,
    PermissionDeniedException,
    UpdateMessageException,
)

message_router = APIRouter()

ws_manager = WebSocketManager()


@message_router.get("/")
async def get_messages(
        chat_id: int,
        params: Params = Depends(),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
) -> Page[MessageResponse]:
    data = await MessageService(user_id, db=db).get_message(chat_id, params)
    return Page(**data)


@message_router.post("/{message_id}/read")
async def mark_message_as_read(
        message_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    try:
        msg_data = await MessageService(user_id=user_id, db=db).update_read_status(message_id=message_id)
        if msg_data.allow_broadcast_msg:
            create_task(
                ws_manager.broadcast_message(
                    msg_data.chat_id,
                    {"reason": "mark_read", "msg_id": msg_data.message_id}
                )
            )
        return {"message_id": msg_data.message_id, "status": "read"}
    except (
            MessageNotFoundException,
            PermissionDeniedException,
            MessageAlreadyReadException,
            UpdateMessageException,
            InternalServerErrorException
    ) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
