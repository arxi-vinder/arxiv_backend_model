from typing import List

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from sqlalchemy.orm import relationship



class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False
    )

    user = relationship(
        "User",
        foreign_keys=[user_id]
    )
    recommendations = Column(JSON, nullable=False)

    relevants: Mapped[List[int]] = mapped_column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User",back_populates="recommendation_logs")