from ast import stmt
from datetime import datetime
from typing import Optional
from sqlalchemy import and_, select, desc, asc
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

    def get_abstracts_batch(self, offset: int = 0, batch_size: int = 100):
        stmt = select(Paper.id, Paper.title, Paper.abstract).offset(offset).limit(batch_size)
        return self.db.execute(stmt).all()

    def get_total_papers_count(self) -> int:
        stmt = select(Paper.id)
        return len(self.db.execute(stmt).scalars().all())

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

    def get_papers_by_category(self, category: str):
        stmt = select(Paper).where(Paper.category == category)
        return self.db.execute(stmt).scalars().all()

    def get_all_categories(self):
        stmt = select(Paper.category.distinct()).order_by(Paper.category)
        return self.db.execute(stmt).scalars().all()

    def get_papers_with_filter(self, limit: int = 100, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, sort_order: str = "newest"):
        stmt = select(Paper)

        if start_date:
            stmt = stmt.where(Paper.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Paper.created_at <= end_date)

        if sort_order == "newest":
            stmt = stmt.order_by(desc(Paper.created_at))
        elif sort_order == "oldest":
            stmt = stmt.order_by(asc(Paper.created_at))

        stmt = stmt.limit(limit)
        return self.db.execute(stmt).scalars().all()

    def search_papers_by_name(self, name: str, limit: int = 100):
        keywords = [word.strip() for word in name.split() if word.strip()]

        conditions = [
            Paper.title.ilike(f"%{keyword}%")
            for keyword in keywords
        ]

        stmt = (
            select(Paper)
            .where(and_(*conditions))
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()