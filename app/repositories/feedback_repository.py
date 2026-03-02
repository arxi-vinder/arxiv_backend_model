from sqlalchemy import func
from sqlmodel import Session

from app.model.feedback import Feedback


class FeedbackRepository():
    def __init__(self, db: Session):
        self.db = db
    
    
    def get_user_feedback(self, user_id: int, paper_id: int):
        return (
            self.db.query(Feedback)
            .filter(
                Feedback.user_id == user_id,
                Feedback.paper_id == paper_id
            )
            .first()
        )

    def create(self, user_id: int, paper_id: int, response: int):
        feedback = Feedback(
            user_id=user_id,
            paper_id=paper_id,
            response=response
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
    
    def update(self, feedback: Feedback, response: int):
        if feedback.response is None:
            feedback.response = 1
        else:
            feedback.response += 1

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        return feedback
    
    def count_total_feedback(self) -> int:
        total = self.db.query(func.count(Feedback.id)).scalar()
        return total or 1
    
    def get_paper_stats(self, paper_id: int):

        reward = self.db.query(func.sum(Feedback.response)).filter(
            Feedback.paper_id == paper_id
        ).scalar() or 0

        total_action = self.db.query(func.count(Feedback.id)).filter(
            Feedback.paper_id == paper_id
        ).scalar() or 0

        return reward, total_action