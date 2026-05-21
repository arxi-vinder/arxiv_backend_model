
from datetime import datetime
from typing import Optional
from app.model.paper import Paper
from app.repositories.paper_repository import PaperRepository
from app.schemas.request.paper_request import PaperCreate, PaperBulkCreate, PaperUpdate
from app.utils.text_preprocessor import preprocess_abstract


class PaperService():

    def __init__(self, repo:PaperRepository):
        self.repo = repo

    def getPaperService(self):
        return self.repo.getPaper()

    def get_paper_id(self, id):
        return self.repo.get_detail_paper(id)

    def create_paper(self, data: PaperCreate) -> Paper:
        paper = Paper(
            title=data.title,
            abstract=preprocess_abstract(data.abstract),
            published_date=data.published_date,
            category=data.category,
            url=data.url,
            author=data.author
        )
        return self.repo.insert_paper(paper)

    def delete_paper(self, id: int) -> Paper | None:
        return self.repo.delete_paper(id)

    def update_paper(self, id: int, data: PaperUpdate) -> Paper | None:
        return self.repo.update_paper(id, data)

    def create_papers_bulk(self, data: PaperBulkCreate) -> list[Paper]:
        papers = [
            Paper(
                title=item.title,
                abstract=preprocess_abstract(item.abstract),
                published_date=item.published_date,
                category=item.category,
                url=item.url,
                author=item.author
            )
            for item in data.papers
        ]
        return self.repo.insert_papers_bulk(papers)

    def get_papers_by_category(self, category: str):
        return self.repo.get_papers_by_category(category)

    def get_all_categories(self):
        return self.repo.get_all_categories()

    def get_papers_with_filter(self, limit: int = 100, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, sort_order: str = "newest"):
        return self.repo.get_papers_with_filter(limit, start_date, end_date, sort_order)

    def search_papers_by_name(self, name: str, limit: int = 100):
        return self.repo.search_papers_by_name(name, limit)