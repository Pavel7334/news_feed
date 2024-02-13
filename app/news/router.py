from _datetime import datetime

from fastapi import APIRouter, status, Depends

from app.database import async_session_maker
from app.news.dao import NewsDAO
from app.news.models import News
from app.news.schemas import SNewsCreate, SNewsList
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/news",
    tags=["Новости"]
)


@router.get("")
async def get_news() -> list[SNewsList]:
    return await NewsDAO.find_all()


#         results=posts,
#         page=page,
#         limit=limit,
#         search_title=search_title,
#         search_username=search_username,
#         filter_date_from=filter_date_from,
#         filter_dates_to=filter_dates_to


@router.get('/{news_id}')
async def get_news_id(
        news_id: int,
):
    async with async_session_maker() as session:
        new_counter = News.views
        new_counter += 1
        await session.commit()
    return await NewsDAO.update(id=news_id, views=new_counter)


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
