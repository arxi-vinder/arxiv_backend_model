from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_db
from app.model.user import User
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.paper_repository import PaperRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.services import recommendation_service
from app.services.recommendation_log_service import RecommendationLogService
from app.services.ucb_service import UCBService
from app.utils.jwt import get_current_user


router = APIRouter(
    prefix='/api/v1'
)


@router.get("/recommend/{paper_id}")
async def get_recommendation(
    paper_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PaperRepository(db)

    service = recommendation_service.RecommendationService(repo)

    results = service.get_recommendations_by_paper_id(
        paper_id,
        top_n
    )

    if not results:
        raise HTTPException(status_code=404, detail="Paper not found")

    feedback_repo = FeedbackRepository(db)

    ucb_service = UCBService(
        feedback_repo=feedback_repo,
        paper_repo=repo,
        cbf_service=service
    )

    final_results = ucb_service.rank_from_list(paper_id)
    log_repo = RecommendationLogRepository(db)
    log_service = RecommendationLogService(log_repo)

    recommendation_ids: list[int] = [int(rec["paper_id"]) for rec in final_results["data"]]  # type: ignore

    existing_log = log_repo.get_latest_by_user(current_user.id)
    if not existing_log or set(recommendation_ids) != set(existing_log.recommendations or []):  # type: ignore
        log_service.create_log(
            user_id=current_user.id,
            recommendations=recommendation_ids,
            relevants=[]
        )

    return {
        "status": "success",
        "message": "Recommendations retrieved successfully",
        "data": {
            "paper_id": paper_id,
            "recommendations": final_results
        }
    }