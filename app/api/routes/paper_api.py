
import traceback
from fastapi import APIRouter, Depends, HTTPException,status
from sqlmodel import Session

from app.db.database import get_db
from app.repositories.paper_repository import PaperRepository
from app.schemas.response.paper_response import PaperResponse
from app.services import recommendation_service
from app.services.paper_service import PaperService


router = APIRouter(
    prefix='/api/v1'
)


@router.get("/papers",response_model=list[PaperResponse])
def get_papers(db:Session = Depends(get_db)):
    try:
        repo = PaperRepository(
            db
        )    
        paper = PaperService(
            repo
        )
        datas = paper.getPaperService()

        if not datas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=[]
            )
        
        return datas
    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
        )

@router.get("/paper/{id}")
def get_detail_paper(id,db:Session = Depends(get_db)):
    
    try:
        repo = PaperRepository(
            db
        )
        
        paper_detail  = PaperService(
            repo
        )
        
        found_paper = paper_detail.get_paper_id(id)
        return {
            "status":"success",
            "detail":found_paper
        }
    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
        )