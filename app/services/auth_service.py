from fastapi import Depends
from sqlmodel import Session

from app.db.database import get_db


# def login(db:Session = Depends(
#     get_db
# )):
#     pass