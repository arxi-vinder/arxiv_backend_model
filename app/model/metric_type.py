from sqlalchemy import Column, DateTime, Integer, String
from app.db.database import Base
import datetime

class MetricType(Base):
    __tablename__="metric_type"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    
    metric_evaluation_name = Column(
        String,
    )
    
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )