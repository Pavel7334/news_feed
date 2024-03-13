from fastapi import HTTPException
from sqlalchemy import update, select, exists, and_, delete, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.news.models import News, Vote, Favourites
from app.users.models import User


class NewsDAO(BaseDAO):
    model = News

    @classmethod
    async def has_user_voted(cls, news_id: int, user_id: int, voted: bool):
        async with async_session_maker() as session:
            query = (
                select(Vote)
                .where(
                    and_(
                        Vote.author_id == user_id,
                        Vote.news_id == news_id,
                        Vote.voted == voted
                    )
                )
            )
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def user_has_access_to_news(cls, news_id: int, user_id: int, session: AsyncSession) -> bool:
        async with session.begin_nested():
            query = select(cls.model).where(and_(cls.model.id == news_id, cls.model.author_id == user_id))
            result = await session.execute(query)
            news_by_author = result.scalar()

            if news_by_author:
                return True  # Пользователь является автором новости

            # Если пользователь не автор, проверяем, есть ли у него доступ к новости
            query = select(cls.model).where(and_(cls.model.id == news_id, cls.model.favourites == True))
            result = await session.execute(query)
            news_with_access = result.scalar()

            return bool(news_with_access)  # Возвращаем True, если есть доступ, иначе False

    @classmethod
    async def count_votes(cls, news_id: int):
        async with async_session_maker() as session:
            query = select(
                func.sum(
                    case(
                        (Vote.voted == True, 1),
                        else_=0
                    )
                ).label(
                    'plus_count'
                ),
                func.sum(
                    case(
                        (Vote.voted == False, 1),
                        else_=0
                    )
                ).label(
                    'minus_count'
                )
            ).where(Vote.news_id == news_id)

            result = await session.execute(query)
            counts = result.fetchone()

            return counts[0] - counts[1]

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

    @classmethod
    async def get_favourites_for_current_user(cls, current_user: User, session: AsyncSession):
        stmt = select(News).join(Favourites).where(
            Favourites.author_id == current_user.id,
            Favourites.news_id == News.id
        )
        result = await session.execute(stmt)
        favourites = result.scalars().all()
        return favourites

    @classmethod
    async def add_news_to_favourites(cls, news_id: int, current_user: User, session: AsyncSession):
        news = await session.get(News, news_id)
        if news is None:
            raise HTTPException(status_code=404, detail="Такой новости нет")

        existing_favourite = await session.execute(
            select(Favourites).filter(
                Favourites.author_id == current_user.id,
                Favourites.news_id == news_id
            )
        )
        existing_favourite = existing_favourite.scalar_one_or_none()
        if existing_favourite:
            raise HTTPException(status_code=400, detail="Новость уже добавлены в избранное")

        new_favourite = Favourites(
            author_id=current_user.id,
            news_id=news_id
        )
        session.add(new_favourite)
        await session.commit()
        return new_favourite
