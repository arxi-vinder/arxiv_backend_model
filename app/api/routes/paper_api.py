
import traceback
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_db
from app.model.user import User
from app.repositories.paper_repository import PaperRepository
from app.schemas.request.paper_request import PaperCreate, PaperBulkCreate, PaperUpdate
from app.schemas.response.paper_response import PaperResponse
from app.schemas.response.paper_response_status import PaperResponseStatus
from app.services import recommendation_service
from app.services.paper_service import PaperService
from app.utils.jwt import get_current_user


router = APIRouter(
    prefix='/api/v1'
)


@router.get("/papers", response_model=PaperResponseStatus)
def get_papers(
    db: Session = Depends(get_db),
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort: str = "newest"
):
    try:
        repo = PaperRepository(db)
        paper = PaperService(repo)

        datas = paper.get_papers_with_filter(limit, start_date, end_date, sort)

        if not datas:
            return {
                "status": "success",
                "message": "No papers found",
                "data": []
            }

        return {
            "status": "success",
            "data": datas
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )

@router.post("/create/paper", status_code=status.HTTP_201_CREATED)
def create_paper(payload: PaperCreate, db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)
        paper = service.create_paper(payload)
        return {
            "status": "success",
            "data": paper
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.post("/papers/bulk", status_code=status.HTTP_201_CREATED)
def create_papers_bulk(payload: PaperBulkCreate, db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)
        papers = service.create_papers_bulk(payload)
        return {
            "status": "success",
            "inserted": len(papers),
            "data": papers
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.put("/update/paper/{id}")
def update_paper(id: int, payload: PaperUpdate, db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)

        updated = service.update_paper(id, payload)

        if not updated:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Paper with id {id} not found"
                }
            )

        return {
            "status": "success",
            "data": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.delete("/delete/paper/{id}")
def delete_paper(id: int, db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)

        deleted = service.delete_paper(id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Paper with id {id} not found"
                }
            )

        return {
            "status": "success",
            "message": f"Paper with id {id} has been deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/paper/{id}")
def get_detail_paper(id, db: Session = Depends(get_db)):

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


@router.get("/papers/category/{category}", response_model=PaperResponseStatus)
def get_papers_by_category(category: str, db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)

        papers = service.get_papers_by_category(category)

        if not papers:
            return {
                "status": "success",
                "message": f"No papers found for category: {category}",
                "data": []
            }

        return {
            "status": "success",
            "data": papers
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    try:
        repo = PaperRepository(db)
        service = PaperService(repo)

        categories = service.get_all_categories()

        if not categories:
            return {
                "status": "success",
                "message": "No categories found",
                "data": []
            }

        return {
            "status": "success",
            "data": categories
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )