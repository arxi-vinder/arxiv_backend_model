import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_db
from app.model.user import User
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.schemas.request.feedback_user_request import FeedbackRequest
from app.schemas.request.recommendation_log_request import RecommendationLogRequest
from app.services.feedback_service import FeedbackService
from app.services.paper_service import PaperService
from app.services.recommendation_log_service import RecommendationLogService
from app.utils.jwt import get_current_user


router = APIRouter(
    prefix='/api/v1'
)

@router.post("/feedback")
def save_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        repo = FeedbackRepository(
            db
        )
        service = FeedbackService(
            repo
        )

        result = service.send_feedback(
            response=request.response,
            current_user_id=current_user.id,
            paper_id=request.paper_id
        )

        return {
            "status": "success",
            "message": "Feedback saved successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.post("/feedback/log")
def save_feedback_log(
    request: RecommendationLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        repo = RecommendationLogRepository(db)
        service = RecommendationLogService(repo)

        existing_log = repo.get_latest_by_user(current_user.id)
        if existing_log:
            current_relevants = list(existing_log.relevants or [])  # type: ignore
            incoming_relevants = list(request.relevants or [])
            merged_relevants = sorted(set(current_relevants) | set(incoming_relevants))
            log = repo.update_log(
                int(existing_log.id),  # type: ignore
                recommendations=request.recommendations,
                relevants=merged_relevants
            )
            if log is None:
                log = service.create_log(
                    user_id=current_user.id,
                    recommendations=request.recommendations,
                    relevants=request.relevants or []
                )
        else:
            log = service.create_log(
                user_id=current_user.id,
                recommendations=request.recommendations,
                relevants=request.relevants or []
            )

        return {
            "status": "success",
            "message": "Recommendation log saved successfully",
            "data": {
                "id": log.id,
                "user_id": log.user_id,
                "recommendations": log.recommendations,
                "relevants": log.relevants,
                "created_at": log.created_at
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )
        
@router.delete("/feedback/delete")
def delete_all_feedback(
    db: Session = Depends(get_db),
    ):
    try:
        repo = FeedbackRepository(
            db
        )
        service = FeedbackService(
            repo
        )

        service.delete_feedback_user()
        
        return {
            "status":"success",
            "message": "All feedback deleted"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )