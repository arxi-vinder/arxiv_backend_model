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

    def _mean_reward(self, rewards):
        if not rewards:
            return 0.0
        return sum(rewards) / len(rewards)

    def calculate_ucb(self, rewards, t):

        s = len(rewards)

        if s == 0:
            return 0.0

        t = max(t, 2)

        mean = self._mean_reward(rewards)

        exploration = math.sqrt(
            (2 * math.log(t)) / s
        )

        return mean + exploration

    def rank_from_list(self, paper_id: int, top_k: int = 5, candidate_size: int = 20):

        candidate_size = max(candidate_size, top_k)

        cbf_candidates = self.cbf_service.get_recommendations_by_paper_id(
            paper_id,
            top_n=candidate_size
        )["recommendations"]

        if not cbf_candidates:
            return {
                "recommendations": [],
                "all_ranked": []
            }

        candidate_ids = [item["id"] for item in cbf_candidates]

        
        feedback_stats = {
            cid: self.feedback_repo.get_paper_stats(cid)
            for cid in candidate_ids
        }


        t = self.feedback_repo.count_total_feedback()
        t = max(t, 2)

        ranked = []

        for item in cbf_candidates:
            pid = item["id"]
            title = item.get("title", "")

            reward, total_action = feedback_stats.get(pid, (0, 0))

            
            if total_action == 0:
                ranked.append({
                    "paper_id": pid,
                    "title": title,
                    "cosine_score": float(item["similarity_score"]),
                    "ucb_score": 0.0,
                    "final_score": 0.3 * float(item["similarity_score"]),
                    "mean_reward": 0.0,
                    "views": 0,
                    "clicks": 0
                })
                continue
            
            
            reward = float(reward)
            total_action = float(total_action)
            t = float(t)
            

            mean = reward / total_action

            
            exploration = math.sqrt((2 * math.log(t)) / total_action)

            ucb_score = mean + exploration


            final_score = (0.7 * ucb_score) + (0.3 * float(item["similarity_score"]))

            ranked.append({
                "paper_id": pid,
                "title": title,
                "cosine_score": float(item["similarity_score"]),
                "ucb_score": float(ucb_score),
                "final_score": float(final_score),
                "mean_reward": float(mean),
                "views": total_action,
                "clicks": reward
            })


        ranked.sort(key=lambda x: x["final_score"], reverse=True)

        return {
            "recommendations": ranked[:top_k],
            "all_ranked": ranked
        }