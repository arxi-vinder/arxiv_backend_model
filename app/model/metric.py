from sqlalchemy import Column, DateTime, ForeignKey, Integer
from app.db.database import Base
from sqlalchemy.orm import relationship
import datetime

class Metric(Base):
    __tablename__="metric_revaluation"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    metric_score = Column(
        Integer,
        index=True
    )
    
    feedback_id = Column(
        Integer,
        ForeignKey(
            "feedback.id"
        )
    )
    
    feedback = relationship(
        "Feedback",
        foreign_keys=[
            feedback_id
        ]
    )
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )