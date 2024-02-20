from sqlalchemy import select, insert, delete, update, desc

from app.database import async_session_maker
from app.news.models import News
from app.news.schemas import SNewsFilter


class BaseDAO:
    model = None

    @classmethod
    def sorting_query(cls, query, filters):
        if filters.sort_by == 'rating':
            if filters.sort_order == 'asc':
                query = query.order_by(cls.model.rating)
            elif filters.sort_order == 'desc':
                query = query.order_by(desc(cls.model.rating))
        if filters.sort_by == 'created_at':
            if filters.sort_order == 'asc':
                query = query.order_by(cls.model.created_at)
            elif filters.sort_order == 'desc':
                query = query.order_by(desc(cls.model.created_at))
        return query

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_all(cls, filters: SNewsFilter, skip: int = 0, limit: int = 10):
        # print(type(filters))
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).offset(skip).limit(limit)
            query = cls.sorting_query(query, filters)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update(cls, id: int, **data):
        async with async_session_maker() as session:
            query = update(cls.model).filter_by(id=id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.fetchone()[0]

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()
