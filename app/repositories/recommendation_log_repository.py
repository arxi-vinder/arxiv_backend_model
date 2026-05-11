from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.model.recommendation_log import RecommendationLog



class RecommendationLogRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        user_id: int,
        recommendations: list[int],
        relevants: list[int] | None = None
    ):
        try:
            log = RecommendationLog(
                user_id=user_id,
                recommendations=recommendations,
                relevants=relevants or []
            )

            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)

            return log

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def save_bulk(self, logs: list[dict]):
        try:
            objs = [
                RecommendationLog(
                    user_id=log["user_id"],
                    recommendations=log["recommendations"],
                    relevants=log.get("relevants", [])
                )
                for log in logs
            ]

            self.db.add_all(objs)
            self.db.commit()

            return objs

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_relevants(self, log_id: int, relevants: list[int]):
        try:
            log = self.get_by_id(log_id)
            if not log:
                return None

            log.relevants = relevants  # type: ignore
            self.db.commit()
            self.db.refresh(log)

            return log

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_log(self, log_id: int, recommendations: list[int], relevants: list[int]):
        try:
            log = self.get_by_id(log_id)
            if not log:
                return None

            log.recommendations = recommendations  # type: ignore
            log.relevants = relevants  # type: ignore
            self.db.commit()
            self.db.refresh(log)

            return log

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_by_id(self, log_id: int):
        return (
            self.db.query(RecommendationLog)
            .filter(RecommendationLog.id == log_id)
            .first()
        )

    def get_all(self):
        return self.db.query(RecommendationLog).all()

    def get_by_user(self, user_id: int):
        return (
            self.db.query(RecommendationLog)
            .filter(RecommendationLog.user_id == user_id)
            .all()
        )

    def get_latest_by_user(self, user_id: int):
        return (
            self.db.query(RecommendationLog)
            .filter(RecommendationLog.user_id == user_id)
            .order_by(RecommendationLog.created_at.desc())
            .first()
        )

    def delete(self, log_id: int):
        try:
            log = self.get_by_id(log_id)
            if not log:
                return False

            self.db.delete(log)
            self.db.commit()
            return True

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_all(self):
        try:
            self.db.query(RecommendationLog).delete()
            self.db.commit()

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_unique_user_count(self):
        """Get count of unique users in recommendation_logs table"""
        try:
            from sqlalchemy import func
            return self.db.query(func.count(func.distinct(RecommendationLog.user_id))).scalar() or 0
        except SQLAlchemyError:
            return 0