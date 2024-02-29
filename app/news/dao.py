from sqlalchemy import update, select, exists, and_, delete

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.news.models import News, Vote


class NewsDAO(BaseDAO):
    model = News

    @classmethod
    async def has_user_voted(cls, news_id: int, user_id: int, voted: bool):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                and_(cls.model.id == news_id, cls.model.author_id == user_id, Vote.voted == voted))
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def upvote(cls, news_id: int):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == news_id).values(rating=cls.model.rating + 1)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def downvote(cls, news_id: int):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == news_id).values(rating=cls.model.rating - 1)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def remove_vote(cls, news_id: int, user_id: int):
        async with async_session_maker() as session:
            # Уменьшить рейтинг новости
            query_update_rating = update(cls.model).where(cls.model.id == news_id).values(rating=cls.model.rating - 1)
            await session.execute(query_update_rating)

            # Удалить запись об оценке пользователя
            query_remove_vote = delete(Vote).where(and_(Vote.author_id == user_id, Vote.news_id == news_id))
            await session.execute(query_remove_vote)

            await session.commit()

    # @classmethod
    # async def update_views(cls, news_id: int, session):
    #     query = update(cls.model).where(cls.model.id == news_id).values(views=cls.model.views + 1).returning(cls.model)
    #     result = await session.execute(query)
    #     await session.commit()
    #     return result.scalar()
