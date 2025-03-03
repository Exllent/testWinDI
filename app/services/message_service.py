from typing import Self, NamedTuple, Optional
from datetime import datetime

from fastapi import status
from fastapi_pagination import Params
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import logger
from app.repositories import MessageRepository
from app.models import Message, MessageReadStatus, ChatTypeEnum
from app.exceptions import (
    InternalServerErrorException,
    MessageNotFoundException,
    MessageAlreadyReadException,
    PermissionDeniedException,
    UpdateMessageException,
)


class MessageData(NamedTuple):
    chat_id: int
    message_id: Optional[int]
    allow_broadcast_msg: bool


class MessageService:
    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.session = db

    async def _update_msg_read_status_group(self, message_id: int, update_msg: bool) -> Optional[int]:
        filter_data = {"message_id": message_id, "user_id": self.user_id}
        message_repository = MessageRepository(session=self.session, model=MessageReadStatus)
        msg_id = await message_repository.update_by_data(filter_data, {"has_read": True}, commit=not update_msg)
        if msg_id is None:
            raise UpdateMessageException(
                message="MessageReadStatus update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        if not update_msg:
            return None

        message_repository.model = Message
        message_id = await message_repository.update_by_data({"id": message_id}, {"is_read": True})

        if message_id is None:
            raise UpdateMessageException(
                message="Message update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return message_id

    async def _update_msg_read_status_person(self, message_id: int) -> int:
        filter_data = {"id": message_id}
        message_id = await MessageRepository(self.session).update_by_data(filter_data, {"is_read": True})
        if message_id is None:
            raise UpdateMessageException(
                message="Message update failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return message_id

    async def update_read_status(self, message_id: int) -> MessageData:
        try:
            message = await MessageRepository(session=self.session).get_message_with_chat_and_read_status(
                message_id=message_id,
                user_id=self.user_id,
            )
            if message is None:
                raise MessageNotFoundException(
                    message=f"Message by message_id: {message} not found",
                    status_code=404
                )

            if message.sender_id == self.user_id:
                raise PermissionDeniedException(
                    message="You cannot perform this action on your own message",
                    status_code=403
                )

            if message.has_read or message.is_read:
                raise MessageAlreadyReadException(
                    message="The message has already been read",
                    status_code=400
                )

            if message.type == ChatTypeEnum.group:
                update_msg = message.unread_count == 1
                message_id = await self._update_msg_read_status_group(message_id=message_id, update_msg=update_msg)
            else:
                update_msg = True
                message_id = await self._update_msg_read_status_person(message_id=message_id)
            message_data = MessageData(chat_id=message.chat_id, message_id=message_id, allow_broadcast_msg=update_msg)
            return message_data
        except SQLAlchemyError as e:
            logger.error(
                "Database error while update read status for msg: %s\n"
                "message_id=%s\n"
                "user_id=%s", str(e), message_id, self.user_id
            )
            raise InternalServerErrorException(
                "An internal error occurred. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_message(self: Self, chat_id: int, params: Params, timestamp: datetime) -> dict:
        limit = params.size
        offset = (params.page - 1) * params.size
        message_repository = MessageRepository(session=self.session)
        query_data = {
            "chat_id": chat_id,
            "timestamp": timestamp.replace(tzinfo=None),
            "order_by": "timestamp",
            "offset": offset,
            "limit": limit
        }
        messages = await message_repository.get_messages_with_paginate(query_data=query_data)
        total = await message_repository.count_total({"chat_id": chat_id})
        return {
            "items": messages,
            "total": total,
            "page": params.page,
            "size": params.size,
            "pages": (total + limit - 1) // limit
        }
