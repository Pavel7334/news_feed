from fastapi import APIRouter, status

from app.news.dao import NewsDAO
from app.news.schemas import SNewsCreate

router = APIRouter(
    prefix="/news",
    tags=["Новости"]
)


@router.post("/news", status_code=201)
async def add_news(news: SNewsCreate):
    await NewsDAO.create(
        title=news.title,
        author_id=news.author_id,
        summary=news.summary,
        description=news.description,
        favourites=news.favourites,
        estimation=news.estimation,
        rating=news.rating,
    )
