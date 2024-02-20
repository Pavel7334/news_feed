from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

DATABASE_URL = "postgresql+psycopg2://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    rating = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class NewsResponse(Base):
    id: int
    title: str
    content: str
    rating: int

@app.put("/news/upvote/{news_id}", response_model=NewsResponse)
def upvote_news(news_id: int):
    db = SessionLocal()
    db_news = db.query(News).filter(News.id == news_id).first()
    if db_news:
        db_news.rating += 1
        db.commit()
        db.refresh(db_news)
        db.close()
        return db_news
    db.close()
    raise HTTPException(status_code=404, detail="News not found")

@app.put("/news/downvote/{news_id}", response_model=NewsResponse)
def downvote_news(news_id: int):
    db = SessionLocal()
    db_news = db.query(News).filter(News.id == news_id).first()
    if db_news:
        db_news.rating -= 1
        db.commit()
        db.refresh(db_news)
        db.close()
        return db_news
    db.close()
    raise HTTPException(status_code=404, detail="News not found")