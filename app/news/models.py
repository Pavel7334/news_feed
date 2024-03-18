from datetime import datetime
from sqlalchemy import MetaData, TIMESTAMP, Boolean, DateTime, JSON, Column, ForeignKey, Integer, String, func, select

from app.database import Base, async_session_maker
from transliterate import slugify

metadata = MetaData()


class News(Base):
    __tablename__ = 'news'

    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    summary = Column(String(250), nullable=False)
    description = Column(String, nullable=False)
    views = Column(Integer, default=0)
    estimation = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    slug = Column(String, nullable=False, unique=True,  server_default="")

    # Метод для генерации slug из заголовка новости
    def generate_slug(self):
        self.slug = slugify(self.title)

    async def save(self):
        async with async_session_maker() as session:
            session.add(self)
            await session.commit()


class Vote(Base):
    __tablename__ = 'votes'

    author_id = Column(Integer, ForeignKey('users.id'))
    news_id = Column(Integer, ForeignKey('news.id'))
    voted = Column(Boolean, default=False)


class Favourites(Base):
    __tablename__ = 'favourites'

    author_id = Column(Integer, ForeignKey('users.id'))
    news_id = Column(Integer, ForeignKey('news.id'))
