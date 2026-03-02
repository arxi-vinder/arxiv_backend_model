import datetime
from app.db.database import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"
    
    
    id : Mapped[int] = mapped_column(
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
    
    # role = Column(
    #     Integer,
    #     unique=True,
    #     index =True
    # )
    
    created_at = Column(
        DateTime, 
        default=datetime.datetime.now
    )
    
    feedbacks = relationship("Feedback", back_populates="user")