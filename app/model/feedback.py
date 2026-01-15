from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from app.db.database import Base
from sqlalchemy.orm import relationship
import datetime

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    feedback_response = Column(
        Integer,
        index=True,
        nullable=False
    )
    
    user_id = Column(
        Integer,
        ForeignKey(
            "user.id"
        )
    )

    paper_id = Column(
        Integer,
        ForeignKey(
            "paper.id"
        )
    )

    user = relationship(
        "User",
        foreign_keys=[user_id]
    )
    
    paper = relationship(
        "Paper",
        foreign_keys=[paper_id]
    )
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )