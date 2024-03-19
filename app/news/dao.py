from fastapi import HTTPException
from sqlalchemy import update, select, exists, and_, delete, func, case
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.news.models import News, Vote, Favourites
from app.users.models import User


class NewsDAO(BaseDAO):
    model = News

    @staticmethod
    async def remove_news_from_favourites(news_id: int, current_user: User):
        async with async_session_maker() as session:
            try:
                # Проверяем, существует ли избранная новость для данного пользователя
                stmt = delete(Favourites).where(
                    Favourites.author_id == current_user.id,
                    Favourites.news_id == news_id
                )

                # Выполняем запрос на удаление
                result = await session.execute(stmt)
                await session.commit()

                # Проверяем, была ли удалена избранная новость
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Новость не найдена в избранном пользователя")

                return {"deleted_news_id": news_id}
            except HTTPException as exc:
                raise exc
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc))

    @staticmethod
    async def get_news_by_slug(slug: str):
        async with async_session_maker() as session:
            news = await session.execute(select(News).filter(News.slug == slug))
            return news.scalar_one_or_none()

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

            if counts is None:
                return 0

            return (counts[0] or 0) - (counts[1] or 0)

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

    # Создаем асинхронный метод класса NewsDAO для получения списка избранных новостей для текущего пользователя
    @classmethod
    async def get_favourites_for_current_user(cls, current_user: User):
        # Используем контекстный менеджер для создания асинхронной сессии с базой данных
        async with async_session_maker() as session:
            # Создаем запрос SQLALchemy для выборки новостей, присоединяем таблицу избранных и фильтруем по идентификатору текущего пользователя
            stmt = select(News).join(Favourites).where(
                Favourites.author_id == current_user.id,
                Favourites.news_id == News.id
            )
            # Выполняем запрос к базе данных и получаем результаты
            result = await session.execute(stmt)
            # Преобразуем результаты в список объектов новостей
            favourites = result.scalars().all()
        # Возвращаем список избранных новостей для текущего пользователя
        return favourites

    # Создаем асинхронный метод класса NewsDAO для добавления новости в избранное для текущего пользователя
    @classmethod
    async def add_news_to_favourites(cls, news_id: int, current_user: User):
        # Используем контекстный менеджер для создания асинхронной сессии с базой данных
        async with async_session_maker() as session:
            # Получаем объект новости по ее идентификатору из базы данных
            news = await session.get(News, news_id)
            # Проверяем, существует ли новость с данным идентификатором
            if news is None:
                # Если новость не найдена, выбрасываем исключение с кодом статуса 404
                raise HTTPException(status_code=404, detail="Такой новости нет")

            # Проверяем, добавлена ли уже данная новость в избранное для текущего пользователя
            existing_favourite = await session.execute(
                select(Favourites).filter(
                    Favourites.author_id == current_user.id,
                    Favourites.news_id == news_id
                )
            )
            existing_favourite = existing_favourite.scalar_one_or_none()
            # Если новость уже добавлена в избранное, выбрасываем исключение с кодом статуса 400
            if existing_favourite:
                raise HTTPException(status_code=400, detail="Новость уже добавлена в избранное")

            # Создаем новый объект избранной новости для текущего пользователя
            new_favourite = Favourites(
                author_id=current_user.id,
                news_id=news_id
            )
            # Добавляем новую избранную новость в сессию базы данных
            session.add(new_favourite)
            # Применяем изменения к базе данных
            await session.commit()
        # Возвращаем новую избранную новость
        return new_favourite
