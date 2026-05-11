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
        reward = float(reward)
        total_action = float(total_action)


        if total_action == 0:
            return 0.0

        t = float(max(t, 2))

        mean = self._mean_reward(reward, total_action)

        exploration = self.alpha * math.sqrt(
            (math.log10(t)) / total_action
        )

        return mean + exploration



    def rank_from_list(self, paper_id: int, top_k: int = 10, candidate_size: int = 20):
        candidate_size = max(candidate_size, top_k)

        cbf_candidates = self.cbf_service.get_recommendations_by_paper_id(
            paper_id,
            top_n=candidate_size
        )["recommendations"]

        if not cbf_candidates:
            return {"data": [], "precision": {}}

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

        t = self.feedback_repo.count_total_feedback() + 1

        ranked = []

        for item in unique_candidates:
            pid = item["id"]
            title = item.get("title", "")

            reward, total_action = feedback_stats.get(pid, (0, 0))

            ucb_score = self.calculate_ucb(reward, total_action, t)

            ctr = reward / total_action if total_action > 0 else 0

            ranked.append({
                "paper_id": pid,
                "title": title,
                "cosine_score": float(item["similarity_score"]),
                "ucb_score": float(ucb_score),
                "views": int(total_action),
                "clicks": int(reward),
                "t": t,
            })


        ranked.sort(key=lambda x: x["ucb_score"], reverse=True)

        return {
            "data": ranked[:top_k],
        }