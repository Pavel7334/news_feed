from fastapi import APIRouter, Depends, Query

from app.database import async_session_maker
from app.news.dao import NewsDAO
from app.news.models import News
from app.news.schemas import SNewsCreate, SNewsList, SNewsFilter, SNewsListWithPagination
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
    async with async_session_maker() as session:
        news = await NewsDAO.get_news_by_id(news_id, session)
        if not news:
            return {'error': 'Статья не найдена'}

        updated_news = await NewsDAO.update_views(news_id, session)

        return {
            'id': updated_news.id,
            'title': updated_news.title,
            'summary': updated_news.summary,
            'views': updated_news.views,
            'rating': updated_news.rating
        }


# @router.get('/{news_id}')
# async def get_news_id(
#         news_id: int,
# ):
#     async with async_session_maker() as session:
#         new_counter = News.views
#         new_counter += 1
#         await session.commit()
#     return await NewsDAO.update(id=news_id, views=new_counter)


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
