import uuid

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logger
from app.models import Chat, ChatTypeEnum
from app.repositories import ChatRepository, GroupRepository
from app.schemas import GroupChatJoin
from app.exceptions import (
    ChatAlreadyExistsException,
    InternalServerErrorException,
    ChatNotFoundException,
    ChatOwnerException,
    UserAlreadyExistsException
)


class ChatService:
    def __init__(self, db: AsyncSession, user_id: int):
        self.session = db
        self.user_id = user_id

    async def create_personal_chat(self, chat_data: dict) -> int:
        chat_data['name'] = str(uuid.uuid4())
        chat_id = await ChatRepository(session=self.session).create_one(chat_data)
        if chat_id is None:
            raise ChatAlreadyExistsException(
                message=f"Personal chat with this name {chat_data['name']} already exists"
            )
        return chat_id

    async def create_group_chat(self, chat_data: dict) -> int:
        async with self.session.begin():
            try:
                chat_data.pop("recipient_id")
                chat_id = await ChatRepository(session=self.session).create_one(chat_data, commit=False)
                if chat_id is None:
                    raise ChatAlreadyExistsException(
                        message=f"Group chat with this name {chat_data['name']} already exists"
                    )
                group_data = {"chat_id": chat_id, "user_id": self.user_id}
                group_id = await GroupRepository(session=self.session).create_one(group_data)
                if group_id is None:
                    raise SQLAlchemyError("Failed to add the creator to the group")
                return chat_id
            except SQLAlchemyError as e:
                logger.error(
                    f"Database error while creating group chat: {str(e)}\n"
                    f"chat_data={chat_data}\n"
                    f"group_data={group_data}\n"
                    f"user_id={self.user_id}"
                )
                await self.session.rollback()
                raise InternalServerErrorException(
                    "An internal error occurred. Please try again later.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    async def join_group_chat(self, form_data: GroupChatJoin) -> int:
        data = {"id": form_data.chat_id, "type": ChatTypeEnum.group}
        chat: Chat = await ChatRepository(session=self.session).get_by_data(data=data)
        if chat is None:
            raise ChatNotFoundException(
                f"Chat with ID {form_data.chat_id} not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if chat.owner_id == self.user_id:
            raise ChatOwnerException("You are the owner of the chat and cannot join it.")
        data = {"chat_id": form_data.chat_id, "user_id": self.user_id}
        group_id = await GroupRepository(session=self.session).create_one(data=data)
        if group_id is None:
            raise UserAlreadyExistsException("User already exists")
        return group_id
