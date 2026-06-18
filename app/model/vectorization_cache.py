from sqlalchemy import Column, DateTime, Integer, String, LargeBinary, JSON
from app.db.database import Base
import datetime
from sqlalchemy.orm import Mapped, mapped_column

class VectorizationCache(Base):
    __tablename__ = "vectorization_cache"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    cache_key = Column(String, unique=True, index=True)

    vectors_data = Column(LargeBinary)

    metadata = Column(JSON)

    total_papers = Column(Integer)

    matrix_size = Column(Integer)

    file_size_bytes = Column(Integer)

    created_at = Column(DateTime, default=datetime.datetime.now)

    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
