from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_db
from app.repositories.paper_repository import PaperRepository
from app.services import recommendation_service


router = APIRouter(
    prefix='/api/v1'
)


@router.get("/recommend/{paper_id}")
def get_recommendation(paper_id: int, top_n: int = 5 , db:Session=Depends(get_db)):
    repo = PaperRepository(
            db
        )
        
    service = recommendation_service.RecommendationService(
        repo
    )
    
    results = service.get_recommendations_by_paper_id(paper_id,top_n)

    if not results:
        raise HTTPException(status_code=404, detail="Paper not found")

    return {
        "paper_id": paper_id,
        "recommendations": results
    }