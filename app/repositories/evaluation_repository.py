from sqlmodel import Session

from app.model.evaluation_res import EvaluationResult


class EvaluationRepository():
    
    def __init__(self, db: Session):
        self.db = db
        
    def save_bulk(self, evaluations: list[dict]):
        objs = [
            EvaluationResult(
                user_id=ev["user_id"],
                precision=ev["precision"],
                recall=ev["recall"],
                f1_score=ev["f1_score"],
                mean_average_precision=ev["map_score"],
                k=ev["k"]
            )
            for ev in evaluations
        ]

        self.db.add_all(objs)
        self.db.commit()

        return objs


    def get_all(self):
        return self.db.query(EvaluationResult).all()

    def get_by_user(self, user_id: int):
        return (
            self.db.query(EvaluationResult)
            .filter(EvaluationResult.user_id == user_id)
            .all()
        )

    def delete_all(self):
        self.db.query(EvaluationResult).delete()
        self.db.commit()