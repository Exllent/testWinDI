from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Optional

from sqlalchemy import select, func, insert, update
from sqlalchemy.exc import IntegrityError, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository[T](ABC):

    @abstractmethod
    async def create_one(self, data: dict, commit: bool = True) -> Optional[T]:
        pass

    @abstractmethod
    async def bulk_create(self, data_list: list[dict], commit: bool = True) -> Optional[Iterable[int]]:
        pass

    @abstractmethod
    async def get_by_data(self, data: dict) -> Optional[T]:
        pass

    @abstractmethod
    async def update_by_data(self, filter_data: dict, values: dict, commit: bool = True) -> Optional[T]:
        pass

    @abstractmethod
    async def count_total(self, data: dict) -> int:
        pass

    @abstractmethod
    async def get_all_by_data(self, data: dict) -> list[T]:
        pass


class SQLAlchemyRepository[T](AbstractRepository[T]):

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def create_one(self, data: dict, commit: bool = True) -> Optional[int]:
        try:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await self.session.execute(stmt)
            if commit:
                await self.session.commit()
            return result.scalar_one()
        except IntegrityError:
            return None

    async def bulk_create(self, data_list: list[dict], commit: bool = True) -> Optional[Iterable[int]]:
        try:
            stmt = insert(self.model).returning(self.model.id)
            result = await self.session.execute(stmt, data_list)
            if commit:
                await self.session.commit()
            return result.scalars().all()
        except IntegrityError:
            return None

    async def update_by_data(self, filter_data: dict, values: dict, commit: bool = True) -> T:
        try:
            stmt = update(self.model).filter_by(**filter_data).values(**values).returning(self.model.id)
            result = await self.session.execute(stmt)
            if commit:
                await self.session.commit()
            return result.scalar_one()
        except IntegrityError:
            return None

    async def get_all_by_data(self, data: dict) -> Iterable[T]:
        stmt = select(self.model).filter_by(**data)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_total(self, data: dict) -> int:
        stmt = select(func.count(self.model.id)).filter_by(**data)  # pylint: disable=E1102
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_by_data(self, data) -> Optional[T]:
        try:
            stmt = select(self.model).filter_by(**data)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except MultipleResultsFound:
            return None
