from sqlalchemy import Column, DateTime, Integer, String, Text
from app.db.database import Base
import datetime

class Paper(Base):
    __tablename__="paper"
    
    id = Column (
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    title = Column(
        String,
        index=True
    )

    abstract = Column(
        Text,
        nullable=True
    )

    published_date = Column(
        DateTime
    )
    
    category = Column(
        String,
        index=True
    )
    
    url = Column(
        String,
        index = True
    )
    
    doi = Column(
        String,
        index=True
    )
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )