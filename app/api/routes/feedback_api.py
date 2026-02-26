import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_db


router = APIRouter(
    prefix='/api/v1'
)

@router.get("/feedback/{id}")
def save_feedback(id,db:Session = Depends(get_db)):
    try:
        
        
        
        pass
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