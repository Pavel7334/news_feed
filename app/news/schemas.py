import datetime
from typing import Optional

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


class SNewsList(SNewsBase):
    pass


class SNewsFilter(BaseModel):
    limit: int = 25
    page: int = 1
    # search_title: Optional[str] = None
    # search_username: Optional[str] = None
    # filter_date_from: Optional[datetime] = None
    # filter_date_to: Optional[datetime] = None
    # sort_by: Optional[str] = None
    # sort_order: Optional[str] = None

