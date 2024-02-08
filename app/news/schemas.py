import datetime

from pydantic import BaseModel


class SNewsBase(BaseModel):
    id: int
    title: str
    author_id: int
    summary: str
    description: str
    views: int
    favourites: bool
    estimation: int
    rating: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class SNewsCreate(BaseModel):
    id: int
    title: str
    author_id: int
    summary: str
    description: str
    favourites: bool
    estimation: int
    rating: int

