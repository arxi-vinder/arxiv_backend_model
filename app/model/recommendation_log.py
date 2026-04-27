from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from app.db.database import Base
import datetime
from sqlalchemy.orm import relationship


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)

    user_id = Column(
        Integer, 
        ForeignKey("users.id"), 
        index=True
    )
    
    recommendations = Column(JSON, nullable=False)

    relevants = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="reclogs")