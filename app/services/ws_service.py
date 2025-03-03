from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logger
from app.exceptions import InternalServerErrorException, CreateMessageException, CreateBalkMessageException
from app.models import ChatTypeEnum, MessageReadStatus
from app.repositories import MessageRepository, GroupRepository


class WebSocketService:

    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.session = db

    async def create_message(self, msg_data: dict, chat_type: str) -> int:
        try:
            if chat_type == ChatTypeEnum.group:
                return await self._create_group_message(msg_data=msg_data)
            return await self._create_person_message(msg_data=msg_data)
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while creating message or group message: {str(e)}\n"
                f"message_data={msg_data}\n"
                f"chat_type={chat_type}\n"
                f"user_id={self.user_id}"
            )
            raise InternalServerErrorException(
                "An internal error occurred. Please try again later.",
                4001)

    async def _create_person_message(self, msg_data: dict) -> int:
        msg_id = await MessageRepository(session=self.session).create_one(msg_data)
        if msg_id is None:
            raise CreateMessageException(
                f"Failed to add message by data {msg_data}",
                status_code=4003
            )
        return msg_id

    async def _create_group_message(self, msg_data: dict) -> int:
        data = {"chat_id": msg_data['chat_id']}
        groups = await GroupRepository(session=self.session).get_all_by_data(data=data)
        not_alone = len(groups) != 1

        msg_repository = MessageRepository(session=self.session)
        msg_id = await msg_repository.create_one(msg_data, commit=not not_alone)
        if msg_id is None:
            raise CreateMessageException(
                f"Failed to add message by data {msg_data}",
                status_code=4003
            )

        data_list = [
            {"user_id": group.user_id, "message_id": msg_id}
            for group in groups if group.user_id != self.user_id
        ]
        if not_alone:
            msg_repository.model = MessageReadStatus
            msg_ids = await msg_repository.bulk_create(data_list=data_list)
            if not isinstance(msg_ids, list):
                raise CreateBalkMessageException("Failed to create bulk messages", status_code=4003)
        return msg_id
