# schemas/feedback.py
from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    paper_id: int
    response: int
    recommendations: Optional[list[int]] = None