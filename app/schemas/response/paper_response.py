from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PaperResponse(BaseModel):
    id: int
    title: str
    abstract: Optional[str]
    category: str