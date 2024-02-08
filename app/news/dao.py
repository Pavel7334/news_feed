from app.dao.base import BaseDAO
from app.news.models import News


class NewsDAO(BaseDAO):
    model = News

