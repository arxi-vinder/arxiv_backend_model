from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository


class EvaluationService:

    def __init__(self, eval_repo: EvaluationRepository, rec_log_repo: Optional[RecommendationLogRepository] = None):
        self.eval_repo = eval_repo
        self.rec_log_repo = rec_log_repo

    def precision_at_k(self, recommended, relevant, k):
        rec_k = recommended[:k]
        return len(set(rec_k) & set(relevant)) / k if k > 0 else 0

    def recall_at_k(self, recommended, relevant, k):
        rec_k = recommended[:k]
        return len(set(rec_k) & set(relevant)) / len(relevant) if relevant else 0

    def f1_score(self, p, r):
        return 1 * p * r / (p + r) if (p + r) > 0 else 0

    def average_precision(self, recommended, relevant, k):
        rec_k = recommended[:k]

        if not relevant:
            return 0.0

        score = 0.0
        hit = 0

        for i, item in enumerate(rec_k):
            rel_k = 1 if item in relevant else 0 

            if rel_k:
                hit += 1
                precision_at_k = hit / (i + 1)
                score += precision_at_k * rel_k

        return score / len(relevant)


    def calculate_mean_metrics(self, evaluation_data: list[dict]):
        if not evaluation_data:
            return {
                "precision": 0,
                "recall": 0,
                "f1_score": 0,
                "map": 0
            }

        n = len(evaluation_data)

        mean_precision = sum(d["precision"] for d in evaluation_data) / n
        mean_recall = sum(d["recall"] for d in evaluation_data) / n
        mean_f1 = sum(d["f1_score"] or 0 for d in evaluation_data) / n
        mean_map = sum(d["map_score"] or 0 for d in evaluation_data) / n

        return {
            "precision": mean_precision,
            "recall": mean_recall,
            "f1_score": mean_f1,
            "map": mean_map
        }

    def calculate_average_metrics_from_db(self):
        """
        Calculate average evaluation metrics (range 0-1) based on:
        - Average of metrics from evaluation_results table
        - Divided by count of unique users in recommendation_logs table

        Formula: Average = Sum of metric values / Count of unique users
        Result range: 0-1 (since each individual metric is 0-1)
        """
        if not self.rec_log_repo:
            return None

        unique_user_count = self.rec_log_repo.get_unique_user_count()

        if unique_user_count == 0:
            return {
                "total_users": 0,
                "average_precision": 0.0,
                "average_recall": 0.0,
                "average_f1_score": 0.0,
                "average_map": 0.0
            }

        sum_precision = self.eval_repo.get_sum_precision()
        sum_recall = self.eval_repo.get_sum_recall()
        sum_f1_score = self.eval_repo.get_sum_f1_score()
        sum_map = self.eval_repo.get_sum_map()

        # Calculate averages (results will be in range 0-1)
        avg_precision = sum_precision / unique_user_count
        avg_recall = sum_recall / unique_user_count
        avg_f1_score = sum_f1_score / unique_user_count
        avg_map = sum_map / unique_user_count

        # Ensure values are in 0-1 range (handle any edge cases)
        avg_precision = max(0.0, min(1.0, avg_precision))
        avg_recall = max(0.0, min(1.0, avg_recall))
        avg_f1_score = max(0.0, min(1.0, avg_f1_score))
        avg_map = max(0.0, min(1.0, avg_map))

        return {
            "total_users": unique_user_count,
            "average_precision": round(avg_precision, 4),
            "average_recall": round(avg_recall, 4),
            "average_f1_score": round(avg_f1_score, 4),
            "average_map": round(avg_map, 4)
        }

    def calculate_average_metrics_by_k(self):
        """
        Calculate average evaluation metrics for each k value (range 0-1)
        Returns average precision, recall, f1_score, and map for each k
        """
        if not self.rec_log_repo:
            return None

        unique_user_count = self.rec_log_repo.get_unique_user_count()

        if unique_user_count == 0:
            return {
                "total_users": 0,
                "metrics_by_k": []
            }

        metrics_by_k_data = self.eval_repo.get_metrics_by_k()

        if not metrics_by_k_data:
            return {
                "total_users": unique_user_count,
                "metrics_by_k": []
            }

        metrics_by_k = []

        for row in metrics_by_k_data:
            k = row.k
            count = row.count

            # Calculate averages
            avg_precision = row.sum_precision / count if count > 0 else 0
            avg_recall = row.sum_recall / count if count > 0 else 0
            avg_f1_score = row.sum_f1_score / count if count > 0 else 0
            avg_map = row.sum_map / count if count > 0 else 0

            # Ensure values are in 0-1 range
            avg_precision = max(0.0, min(1.0, avg_precision))
            avg_recall = max(0.0, min(1.0, avg_recall))
            avg_f1_score = max(0.0, min(1.0, avg_f1_score))
            avg_map = max(0.0, min(1.0, avg_map))

            metrics_by_k.append({
                "k": k,
                "average_precision": round(avg_precision, 4),
                "average_recall": round(avg_recall, 4),
                "average_f1_score": round(avg_f1_score, 4),
                "average_map": round(avg_map, 4),
                "count": count
            })

        # Sort by k value
        metrics_by_k.sort(key=lambda x: x["k"])

        return {
            "total_users": unique_user_count,
            "metrics_by_k": metrics_by_k
        }