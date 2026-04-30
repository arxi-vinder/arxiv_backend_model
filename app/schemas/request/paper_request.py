from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaperCreate(BaseModel):
    title: str
    abstract: Optional[str] = None
    published_date: datetime
    category: str
    url: str
    author: str


class PaperBulkCreate(BaseModel):
    papers: list[PaperCreate]


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
