from sqlalchemy import select
from sqlmodel import Session

from app.model.paper import Paper


class PaperRepository():
    
    def __init__(self, db: Session):
        self.db = db

    def getPaper(self):
        stmt = select(Paper)
        return self.db.scalars(
            stmt
        ).all()