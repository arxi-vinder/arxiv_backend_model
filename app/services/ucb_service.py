import math
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.paper_repository import PaperRepository

class UCBService:

    def __init__(self, feedback_repo:FeedbackRepository, paper_repo:PaperRepository, alpha: float = 2.0):
        self.feedback_repo = feedback_repo
        self.paper_repo = paper_repo
        self.alpha = alpha

    def calculate_ucb(self, reward, total_action, t):

        if total_action == 0:
            return 0.0

        reward = float(reward)
        total_action = float(total_action)
        t = float(t)

        exploit = reward

        exploration = math.sqrt(
            (self.alpha * math.log(t + 1)) / total_action
        )

        return exploit + exploration

    def rank_from_list(self, cosine_results: list):

        t = self.feedback_repo.count_total_feedback()
        results = []

        for item in cosine_results:

            reward, total_action = self.feedback_repo.get_paper_stats(
                item["id"]
            )

            ucb_score = self.calculate_ucb(
                reward,
                total_action,
                t
            )

            results.append({
                "paper_id": item["id"],
                "title": item.get("title"),
                "cosine_score": item.get("similarity_score"),
                "reward": reward,
                "total_action": total_action,
                "ucb_score": ucb_score
            })


        results.sort(key=lambda x: x["ucb_score"], reverse=True)

        return results