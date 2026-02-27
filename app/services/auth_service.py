from fastapi import Depends
from sqlmodel import Session
from app.utils.security import hash_pwd,verify_pwd
from app.db.database import get_db
from app.model.user import User
from app.repositories.auth_repository import AuthRepository
from app.utils.security import create_access_token
class AuthService:
    
    def __init__(self,repo:AuthRepository) -> None:
        self.repo = repo

    def register(self,username:str , password:str):
        
        isUserExist = self.repo.get_by_username(username)
        
        if isUserExist:
            return None
        
        
        hashed_pwd = hash_pwd(password)
        
        user = User(
            username = username,
            password = hashed_pwd
        )
        
        self.repo.create_user(user)
        
        token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    def checkIfUserExists(self,username:str):
        return self.repo.get_by_username(username)
    
    def login(self, username: str, password: str):
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_pwd(password, str(user.password)):
            return None

    
        token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
        
        })

        return {
            "access_token": token,
            "username":user.username,
            "id":user.id,
            "token_type": "bearer",
        }