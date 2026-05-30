import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    username = Column(
        String(50),
        unique=False,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # role aligned with the `admin` table migration (String(50), not unique)
    role = Column(
        String(50),
        index=True,
        nullable=False,
        default="admin"
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.now
    )