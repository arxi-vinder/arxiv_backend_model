import math
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.paper_repository import PaperRepository
from app.services.recommendation_service import RecommendationService


class UCBService:

    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        paper_repo: PaperRepository,
        cbf_service: RecommendationService,
        alpha: float = 2.0
    ):
        self.feedback_repo = feedback_repo
        self.paper_repo = paper_repo
        self.cbf_service = cbf_service
        self.alpha = alpha


    def _mean_reward(self, reward, total_action):
        if total_action == 0:
            return 0.0
        return float(reward) / float(total_action)


    def calculate_ucb(self, reward, total_action, t):

        if total_action == 0:
            return 0.0

        reward = float(reward)
        total_action = float(total_action)
        t = float(max(t, 2))

        mean = self._mean_reward(reward, total_action)

        exploration = math.sqrt(
            (2 * math.log(t)) / total_action
        )

        return mean + exploration

    def precision_at_k(self, ranked_items, k: int):

        if k <= 0:
            return 0.0


        top_k = ranked_items[:k]

        if not top_k:
            return 0.0


        relevant = sum(
            1 for item in top_k if item.get("clicks", 0) > 0
        )

        return round(relevant / k, 2)

    def recall_at_k(self, ranked_items, k: int):

        if k <= 0 or not ranked_items:
            return 0.0

        total_relevant = sum(
            1 for item in ranked_items if item.get("clicks", 0) > 0
        )

        if total_relevant == 0:
            return 0.0

        top_k = ranked_items[:k]

        relevant_in_k = sum(
            1 for item in top_k if item.get("clicks", 0) > 0
        )

        return round(relevant_in_k / total_relevant, 2)

    def average_precision(self, ranked_items):

        if not ranked_items:
            return 0.0

        relevant_count = 0
        precision_sum = 0.0

        for k, item in enumerate(ranked_items, start=1):

            if item.get("clicks", 0) > 0:
                relevant_count += 1

                precision_k = self.precision_at_k(ranked_items, k)
                precision_sum += precision_k

        if relevant_count == 0:
            return 0.0

        return round(precision_sum / relevant_count, 3)
    
    def mean_average_precision(self, ranked_items_list):
        """
        ranked_items_list = [
            ranked_user1,
            ranked_user2,
            ...
        ]
        """

        if not ranked_items_list:
            return 0.0

        ap_sum = 0.0

        for ranked_items in ranked_items_list:
            ap_sum += self.average_precision(ranked_items)

        return round(ap_sum / len(ranked_items_list), 3)
    
    def f1_at_k(self, ranked_items, k: int):

        precision = self.precision_at_k(ranked_items, k)
        recall = self.recall_at_k(ranked_items, k)

        if (precision + recall) == 0:
            return 0.0

        f1 = 2 * (precision * recall) / (precision + recall)

        return round(f1, 2)
    
    def precision_multi_k(self, ranked_items):

        return {
            "p@1": self.precision_at_k(ranked_items, 1),
            "p@2": self.precision_at_k(ranked_items, 2),
            "p@3": self.precision_at_k(ranked_items, 3),
            "p@4": self.precision_at_k(ranked_items, 4),
            
        }
        
    def recall_multi_k(self, ranked_items):

        return {
            "r@1": self.recall_at_k(ranked_items, 1),
            "r@2": self.recall_at_k(ranked_items, 2),
            "r@3": self.recall_at_k(ranked_items, 3),
            "r@4": self.recall_at_k(ranked_items, 4),
        }
    def f1_multi_k(self, ranked_items):

        return {
            "f1@1": self.f1_at_k(ranked_items, 1),
            "f1@2": self.f1_at_k(ranked_items, 2),
            "f1@3": self.f1_at_k(ranked_items, 3),
            "f1@4": self.f1_at_k(ranked_items, 4),
        }

    def rank_from_list(
        self,
        paper_id: int,
        top_k: int = 5,
        candidate_size: int = 20
    ):

        candidate_size = max(candidate_size, top_k)

        cbf_candidates = self.cbf_service.get_recommendations_by_paper_id(
            paper_id,
            top_n=candidate_size
        )["recommendations"]

        if not cbf_candidates:
            return {
                "data": [],
                "precision": {}
            }
        seen = set()
        unique_candidates = []

        for item in cbf_candidates:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique_candidates.append(item)

        candidate_ids = [item["id"] for item in unique_candidates]

        feedback_stats = {
            cid: self.feedback_repo.get_paper_stats(cid)
            for cid in candidate_ids
        }

        t = max(self.feedback_repo.count_total_feedback(), 2)

        ranked = []

        for item in unique_candidates:
            pid = item["id"]
            title = item.get("title", "")

            reward, total_action = feedback_stats.get(pid, (0, 0))

            if total_action == 0:
                ranked.append({
                    "paper_id": pid,
                    "title": title,
                    "cosine_score": float(item["similarity_score"]),
                    "ucb_score": 0.0,
                    "views": 0,
                    "clicks": 0,
                    "is_relevant": 0
                })
                continue

            ucb_score = self.calculate_ucb(reward, total_action, t)

            ranked.append({
                "paper_id": pid,
                "title": title,
                "cosine_score": float(item["similarity_score"]),
                "ucb_score": float(ucb_score),
                "views": int(total_action),
                "clicks": int(reward),
                "is_relevant": 1 if reward > 0 else 0
            })

        # ranked.sort(key=lambda x: x["ucb_score"], reverse=True)
        precision_scores = self.precision_multi_k(ranked)
        recall_scores = self.recall_multi_k(ranked)
        f1_scores = self.f1_multi_k(ranked)
        ap_score = self.average_precision(ranked)

        return {
            "data": ranked[:top_k],
            "precision": precision_scores,
            "recall":recall_scores,
            "f1_score":f1_scores,
            "ap_score":ap_score
        }