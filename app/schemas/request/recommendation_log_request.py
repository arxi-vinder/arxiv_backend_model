from typing import Optional

from pydantic import BaseModel


class RecommendationLogRequest(BaseModel):
    recommendations: list[int]
    relevants: Optional[list[int]] = None
