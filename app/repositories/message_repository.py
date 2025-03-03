from typing import Self, Union

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SQLAlchemyRepository
from app.models import Message, MessageReadStatus, Chat


class MessageRepository(SQLAlchemyRepository[Union[Message, MessageReadStatus]]):

    def __init__(
            self: Self,
            session: AsyncSession,
            model: type[Union[Message, MessageReadStatus]] = Message
    ):
        super().__init__(session=session, model=model)

    async def get_message_with_chat_and_read_status(self: Self, message_id: int, user_id: int):
        unread_count_subquery = self._get_unread_count_subquery(message_id=message_id)
        stmt = (
            select(
                Message.chat_id,
                Message.sender_id,
                Message.is_read,
                Chat.type,
                MessageReadStatus.has_read,
                unread_count_subquery
            ).
            join(Chat, Chat.id == Message.chat_id).
            outerjoin(
                MessageReadStatus,
                (Message.id == MessageReadStatus.message_id) & (MessageReadStatus.user_id == user_id)
            ).
            where(Message.id == message_id)
        )
        result = await self.session.execute(stmt)
        return result.mappings().first()

    async def get_messages_with_paginate(self: Self, query_data: dict) -> list[Message]:
        stmt = (
            select(self.model).
            filter((Message.chat_id == query_data['chat_id']) & (Message.timestamp < query_data['timestamp'])).
            order_by(desc(query_data['order_by'])).
            offset(offset=query_data['offset']).
            limit(limit=query_data['limit'])
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    @staticmethod
    def _get_unread_count_subquery(message_id: int):
        return (
            select(func.count().label("unread_count")).
            where((MessageReadStatus.message_id == message_id) & (MessageReadStatus.has_read != True)).
            scalar_subquery().
            label("unread_count")
        )
