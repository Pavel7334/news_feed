from sqlalchemy import select, insert, delete, update, desc, func

from app.database import async_session_maker
from app.news.models import News
from app.news.schemas import SNewsFilter


class BaseDAO:
    model = None
    count = 0

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
    async def find_all(cls, filters: SNewsFilter):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).offset(filters.page-1).limit(filters.limit)
            query = cls.sorting_query(query, filters)
            result = await session.execute(query)
            cls.count = await cls.get_count(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, data):
        async with async_session_maker() as session:
            # Создаем экземпляр модели, передавая данные
            instance = cls.model(**data)
            session.add(instance)
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

    @classmethod
    async def get_count(cls, query) -> int:
        async with async_session_maker() as session:
            query = select(func.count()).select_from(query)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_by_slug(cls, slug: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.slug == slug)
            result = await session.execute(query)
            return result.scalar_one_or_none()
