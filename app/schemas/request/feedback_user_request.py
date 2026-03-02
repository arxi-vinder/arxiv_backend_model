# schemas/feedback.py
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    paper_id: int
    response: int 