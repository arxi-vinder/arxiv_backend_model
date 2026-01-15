import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.db.database import Base

class Admin(Base):
    __tablename__ = "admin"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    username = Column(
        String,
        unique=False,
        index=True
    )
    
    password = Column(
        String,
        unique=True,
        index=True
    )
    
    role = Column(
        Integer,
        unique=True,
        index =True
    )
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )