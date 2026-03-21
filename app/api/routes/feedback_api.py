import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_db
from app.model.user import User
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.request.feedback_user_request import FeedbackRequest
from app.services.feedback_service import FeedbackService
from app.services.paper_service import PaperService
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