import datetime
from typing import Optional, List

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
    title: str
    author_id: int
    summary: str
    description: str
    favourites: bool
    estimation: int
    rating: int


class SNewsList(BaseModel):
    results: list[SNewsBase]


class SNewsFilter(BaseModel):
    page: int = 1
    limit: int = 25
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


class SNewsListWithPagination(BaseModel):
    count: int
    limit: int
    page: int
    last_page: int
    results: List[SNewsBase]
