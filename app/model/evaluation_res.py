import datetime
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class EvaluationResult(Base):
    __tablename__ = 'evaluation_results'

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer, 
        ForeignKey('users.id'), 
        nullable=False
    )

    user = relationship(
        "User",
        foreign_keys=[user_id]
    )
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    mean_average_precision = Column(
        Float, 
        nullable=True
    )
    k = Column(Integer, nullable=True)  

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="evalres")