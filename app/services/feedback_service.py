from fastapi import Depends
from sqlmodel import Session

from app.model.feedback import Feedback
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.paper_repository import PaperRepository

class FeedbackService():
    
    def __init__(self , repo:FeedbackRepository) -> None:
        self.paper_repository = repo
    
    def send_feedback(
        self,
        response: int,
        current_user_id: int,
        paper_id: int
    ) -> Feedback:
        """Ambil cosine , kasi feedback , hitung make skor ucb , ranking """
        if response not in [1, 0]:
            raise ValueError(
                "Feedback must be 1 (like) or 0 (dislike)"
            )


        existing_feedback = self.paper_repository.get_user_feedback(
            user_id=current_user_id,
            paper_id=paper_id
        )

        if existing_feedback:
            return self.paper_repository.update(
                feedback=existing_feedback,
                response=response
            )

        return self.paper_repository.create(
            user_id=current_user_id,
            paper_id=paper_id,
            response=response
        )

    def delete_feedback_user(self):
        return self.paper_repository.delete_all_feedback()