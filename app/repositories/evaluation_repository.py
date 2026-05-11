from sqlmodel import Session

from app.model.evaluation_res import EvaluationResult
from sqlalchemy import func

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

    def get_sum_precision(self):
        """Get sum of all precision values"""
        result = self.db.query(func.sum(EvaluationResult.precision)).scalar()
        return result or 0

    def get_sum_recall(self):
        """Get sum of all recall values"""

        result = self.db.query(func.sum(EvaluationResult.recall)).scalar()
        return result or 0

    def get_sum_f1_score(self):
        """Get sum of all f1_score values"""
        result = self.db.query(func.sum(EvaluationResult.f1_score)).scalar()
        return result or 0

    def get_sum_map(self):
        """Get sum of all mean_average_precision (MAPE) values"""
        result = self.db.query(func.sum(EvaluationResult.mean_average_precision)).scalar()
        return result or 0

    def get_metrics_by_k(self):
        """Get sum and count of metrics grouped by k value"""
        results = self.db.query(
            EvaluationResult.k,
            func.sum(EvaluationResult.precision).label('sum_precision'),
            func.sum(EvaluationResult.recall).label('sum_recall'),
            func.sum(EvaluationResult.f1_score).label('sum_f1_score'),
            func.sum(EvaluationResult.mean_average_precision).label('sum_map'),
            func.count(EvaluationResult.id).label('count')
        ).group_by(EvaluationResult.k).all()

        return results if results else []