
from app.repositories.paper_repository import PaperRepository


class PaperService():
    
    def __init__(self, repo:PaperRepository):
        self.repo = repo

    def getPaperService(self):
        return self.repo.getPaper()