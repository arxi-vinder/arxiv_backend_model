import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_db
from app.repositories.admin_repository import AdminRepository
from app.schemas.request.admin_request import AdminLoginRequest
from app.services.admin_service import AdminService


router = APIRouter(
    prefix='/api/v1'
)


@router.post("/admin/login")
def login(admin: AdminLoginRequest, db: Session = Depends(get_db)):
    try:
        repo = AdminRepository(db)
        service = AdminService(repo)

        token = service.login(
            admin.username,
            admin.password
        )

        if token is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Invalid username or password"
                }
            )

        return {
            "status": "success",
            "message": "Success Login",
            "data": token
        }

    except HTTPException:
        raise
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


@router.post("/admin/logout")
def logout():
    return {
        "status": "success",
        "message": "Logout successful. Please delete token on client side."
    }
