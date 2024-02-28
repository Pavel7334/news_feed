from sqlalchemy import update

from app.dao.base import BaseDAO
from app.news.models import News


class NewsDAO(BaseDAO):
    model = News

    @classmethod
    async def get_news_by_id(cls, news_id: int, session):
        query = await session.execute(cls.model.__table__.select().where(cls.model.id == news_id))
        return query.scalar()

    # @classmethod
    # async def update_views(cls, news_id: int, session):
    #     query = update(cls.model).where(cls.model.id == news_id).values(views=cls.model.views + 1).returning(cls.model)
    #     result = await session.execute(query)
    #     await session.commit()
    #     return result.scalar()
