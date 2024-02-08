from fastapi import FastAPI

from app.news.router import router as router_news

app = FastAPI()


app.include_router(router_news)