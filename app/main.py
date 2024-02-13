from fastapi import FastAPI

from app.news.router import router as router_news
from app.users.router import router as router_users

app = FastAPI()


app.include_router(router_users)
app.include_router(router_news)

