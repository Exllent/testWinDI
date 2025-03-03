from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.core import get_current_user_id, get_db
from app.schemas import GroupChatJoin, CreateChatRequest
from app.services import ChatService
from app.exceptions import (
    ChatAlreadyExistsException,
    InternalServerErrorException,
    ChatNotFoundException,
    ChatOwnerException,
    UserAlreadyExistsException
)

chat_router = APIRouter()


@chat_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_chat(
        form_data: CreateChatRequest,
        user_id: Annotated[int, Depends(get_current_user_id)],
        db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        service = ChatService(db=db, user_id=user_id)
        data = form_data.model_dump()
        data["owner_id"] = user_id
        is_group = form_data.is_group
        chat_id = await service.create_group_chat(data) if is_group else await service.create_personal_chat(data)
        return {"chat_id": chat_id}
    except (ChatAlreadyExistsException, InternalServerErrorException) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@chat_router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_group_chat(
        form_data: GroupChatJoin,
        user_id: Annotated[int, Depends(get_current_user_id)],
        db: AsyncSession = Depends(get_db)
):
    try:
        group_id = await ChatService(db=db, user_id=user_id).join_group_chat(form_data=form_data)
        return {"group_id": group_id}
    except (ChatNotFoundException, ChatOwnerException, UserAlreadyExistsException) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
