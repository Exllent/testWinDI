from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import select, Select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository[T](ABC):

    @abstractmethod
    async def create_one(self, data: dict) -> Optional[T]:
        pass

    @abstractmethod
    async def get_by_data(self, data) -> Optional[T]:
        pass


class SQLAlchemyRepository[T](AbstractRepository[T]):

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def create_one(self, data: dict) -> Optional[int]:
        try:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one()
        except IntegrityError:
            return None

    async def get_by_data(self, data) -> Optional[T]:
        try:
            stmt = select(self.model).filter_by(**data)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except MultipleResultsFound:
            return None

    async def get_by_id(self, obj_id: int) -> Select:
        return select(self.model).filter_by(id=obj_id)

    async def execute_query(self, stmt) -> T | None:
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
