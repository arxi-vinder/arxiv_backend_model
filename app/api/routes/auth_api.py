import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_db
from app.repositories.auth_repository import AuthRepository
from app.schemas.request.auth_request import AuthRequest
from app.services.auth_service import AuthService


router = APIRouter(
    prefix='/api/v1'
)


@router.post("/auth/register")
def register(user:AuthRequest,db:Session = Depends(get_db)):
    try:
        repo = AuthRepository(
            db
        )
        
        service = AuthService(
            repo
        )
        
        if service.checkIfUserExists(user.username):
            return {
                "status":"success",
                "message":"User Already Exists !"
            }
        
        else:            
            token = service.register(
                user.username , 
                user.password
            )
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "data": token
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
        
@router.post("/auth/login")
def login(user:AuthRequest , db:Session = Depends(get_db)):
    try:
        repo = AuthRepository(
            db
        )
        
        service = AuthService(
            repo
        )

        token = service.login(
                user.username , 
                user.password
        )
        
        
        if token is None:
            raise HTTPException(
                status_code=404
            )

        return {
                "status": "success",
                "message": "Success Login",
                "data": token
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

@router.post("/auth/logout")
def logout():
    return {
        "status": "success",
        "message": "Logout successful. Please delete token on client side."
    }