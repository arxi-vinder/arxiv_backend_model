from app.utils.jwt import verify_pwd, create_access_token
from app.repositories.admin_repository import AdminRepository


class AdminService:

    def __init__(self, repo: AdminRepository) -> None:
        self.repo = repo

    def login(self, username: str, password: str):
        admin = self.repo.get_by_username(username)
        if not admin:
            return None
        if not verify_pwd(password, str(admin.password)):
            return None

        token = create_access_token({
            "sub": str(admin.id),
            "username": admin.username,
            "role": admin.role,
        })

        return {
            "access_token": token,
            "username": admin.username,
            "id": admin.id,
            "role": admin.role,
            "token_type": "bearer",
        }
