from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_session

from app.database import async_session_maker
from app.news.dao import NewsDAO
from app.news.models import News, Vote
from app.news.schemas import SNewsCreate, SNewsFilter, SNewsListWithPagination
from app.users.dependencies import get_current_user
from app.users.models import User
from math import ceil

router = APIRouter(
    prefix="/news",
    tags=["Новости"]
)


@router.get("", response_model=SNewsListWithPagination)
async def get_news(
        filters: SNewsFilter = Depends()
) -> SNewsListWithPagination:
    news = await NewsDAO.find_all(filters)
    news_count = NewsDAO.count

    total_pages = ceil(news_count / filters.limit)
    current_page = filters.page // filters.limit + 1 if filters.limit > 0 else 1

    return SNewsListWithPagination(
        count=news_count,
        limit=filters.limit,
        page=current_page,
        last_page=total_pages,
        results=news,
    )


@router.get('/{news_id}')
async def get_news_id(news_id: int):
    news = await NewsDAO.find_one_or_none(id=news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Такой новости нет")
    new_counter = News.views
    new_counter += 1

    updated_news = await NewsDAO.update(news_id, views=new_counter)
    # Вызываем метод count_votes для получения количества голосов
    votes_count = await NewsDAO.count_votes(news_id)

    return {
        'id': updated_news.id,
        'title': updated_news.title,
        'summary': updated_news.summary,
        'views': updated_news.views,
        'rating': votes_count
    }


@router.delete("/{news_id}")
async def remove_news(
        news_id: int,
):
    await NewsDAO.delete(id=news_id)


@router.post("/news", status_code=201)
async def add_news(news: SNewsCreate, user: User = Depends(get_current_user)):
    await NewsDAO.create(
        author_id=user.id,
        title=news.title,
        summary=news.summary,
        description=news.description,
        favourites=news.favourites,
        estimation=news.estimation,
        rating=news.rating,
    )


@router.post("/{news_id}/up_vote", status_code=200)
async def up_vote_news(news_id: int, user: User = Depends(get_current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            # Проверить, что пользователь еще не голосовал за эту новость
            if await NewsDAO.has_user_voted(news_id, user.id, voted=True):
                raise HTTPException(status_code=400, detail="Вы уже голосовали за эту новость")

            # Проверить, есть ли уже запись в таблице votes
            existing_vote = await session.execute(select(Vote).where(and_(Vote.news_id == news_id, Vote.author_id == user.id)))
            existing_vote = existing_vote.scalar()

            # Если запись уже существует, обновить ее
            if existing_vote:
                existing_vote.voted = True
            else:
                # Иначе, добавить новую запись
                new_vote = Vote(news_id=news_id, author_id=user.id, voted=True)
                session.add(new_vote)

    return {"message": "Рейтинг повышен успешно"}


@router.post("/{news_id}/down_vote", status_code=200)
async def down_vote_news(news_id: int, user: User = Depends(get_current_user)):
    async with async_session_maker() as session:
        async with session.begin():
            # Проверить, что пользователь еще не голосовал за эту новость
            if await NewsDAO.has_user_voted(news_id, user.id, voted=False):
                raise HTTPException(status_code=400, detail="Вы уже голосовали за эту новость")

            # Проверить, есть ли уже запись в таблице votes
            existing_vote = await session.execute(select(Vote).where(and_(Vote.news_id == news_id, Vote.author_id == user.id)))
            existing_vote = existing_vote.scalar()

            # Если запись уже существует, обновить ее
            if existing_vote:
                existing_vote.voted = False
            else:
                # Иначе, добавить новую запись
                new_vote = Vote(news_id=news_id, author_id=user.id, voted=False)
                session.add(new_vote)

    return {"message": "Рейтинг понижен успешно"}
