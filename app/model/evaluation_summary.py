from sqlalchemy import Column, Integer, Float, String, DateTime
from app.db.database import Base
import datetime


class EvaluationSummary(Base):
    __tablename__ = "evaluation_summary"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, index=True)
    source_paper_id = Column(Integer)

    session_id = Column(String, index=True)


    p_at_1 = Column(Float)
    p_at_2 = Column(Float)
    p_at_3 = Column(Float)
    p_at_4 = Column(Float)


    r_at_1 = Column(Float)
    r_at_2 = Column(Float)
    r_at_3 = Column(Float)
    r_at_4 = Column(Float)

    # 🔥 F1 Score
    f1_at_1 = Column(Float)
    f1_at_2 = Column(Float)
    f1_at_3 = Column(Float)
    f1_at_4 = Column(Float)

    # 🔥 AP & MAP
    ap_score = Column(Float)
    map_score = Column(Float, nullable=True)

    total_recommended = Column(Integer)
    total_relevant = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )