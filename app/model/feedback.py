from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    response: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )
    
    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        )
    )

    paper_id = Column(
        Integer,
        ForeignKey(
            "papers.id"
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
    
    user = relationship("User", back_populates="feedbacks")