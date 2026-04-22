from sqlalchemy import select
from sqlmodel import Session

from app.model.paper import Paper


class PaperRepository():
    
    def __init__(self, db: Session):
        self.db = db


    def getPaper(self, limit: int = 100):
        stmt = select(Paper).limit(limit)
        return self.db.execute(stmt).all()


    def get_detail_paper(self, id: int):
        return self.db.get(Paper, id)

    def get_abstracts(self, limit: int = 100):
        stmt = select(Paper.id, Paper.title, Paper.abstract).limit(limit)
        return self.db.execute(stmt).all()