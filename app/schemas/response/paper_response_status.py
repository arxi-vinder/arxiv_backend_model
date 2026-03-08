from pydantic import BaseModel
from typing import List

from app.schemas.response.paper_response import PaperResponse

class PaperResponseStatus(BaseModel):
    status: str
    data: List[PaperResponse]