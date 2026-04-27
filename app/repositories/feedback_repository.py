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
                feedback.response = 0

        if response == 1:
                feedback.response += 1

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        return feedback

    def get_user_liked_paper_ids(self, user_id: int) -> list[int]:
        liked_rows = (
            self.db.query(Feedback.paper_id)
            .filter(
                Feedback.user_id == user_id,
                Feedback.response == 1
            )
            .all()
        )
        return list({row[0] for row in liked_rows})
    
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

    def delete_all_feedback(self):
        self.db.query(Feedback).delete()
        self.db.commit()