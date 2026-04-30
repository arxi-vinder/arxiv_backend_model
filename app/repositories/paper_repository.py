from sqlalchemy import select
from sqlmodel import Session

from app.model.paper import Paper
from app.schemas.request.paper_request import PaperUpdate


class PaperRepository():

    def __init__(self, db: Session):
        self.db = db


    def getPaper(self, limit: int = 100):
        stmt = select(Paper).limit(limit)
        return self.db.execute(stmt).scalars().all()


    def get_detail_paper(self, id: int):
        return self.db.get(Paper, id)

    def get_abstracts(self, limit: int = 100):
        stmt = select(Paper.id, Paper.title, Paper.abstract).limit(limit)
        return self.db.execute(stmt).all()

    def insert_paper(self, paper: Paper) -> Paper:
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper

    def insert_papers_bulk(self, papers: list[Paper]) -> list[Paper]:
        self.db.add_all(papers)
        self.db.commit()
        for paper in papers:
            self.db.refresh(paper)
        return papers

    def delete_paper(self, id: int) -> Paper | None:
        paper = self.db.get(Paper, id)
        if not paper:
            return None
        self.db.delete(paper)
        self.db.commit()
        return paper

    def update_paper(self, id: int, data: PaperUpdate) -> Paper | None:
        paper = self.db.get(Paper, id)
        if not paper:
            return None
        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(paper, field, value)
        self.db.commit()
        self.db.refresh(paper)
        return paper