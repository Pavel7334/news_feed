from datetime import datetime
from sqlalchemy import MetaData, TIMESTAMP, Boolean, DateTime, JSON, Column, ForeignKey, Integer, String
from app.database import Base

metadata = MetaData()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(Integer, ForeignKey('user.id'))
    summary = Column(String(250), nullable=False)
    description = Column(String, nullable=False)
    views = Column(Integer, default=0)
    favourites = Column(Boolean, default=False)
    estimation = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

