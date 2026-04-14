from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import UserInfo

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(request: Request) -> UserInfo:
    """
    FastAPI dependency — reads user from session.
    Use on routes that require a logged-in user.

        @app.get("/me")
        def me(user: UserInfo = Depends(get_current_user)):
            return user
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return UserInfo(**user_data)


def require_groups(*groups: str):
    """
    FastAPI dependency factory — requires user to be in at least one of the given groups.

        @app.get("/admin")
        def admin(user: UserInfo = Depends(require_groups("admin", "superuser"))):
            return user
    """
    def _check(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        if not any(g in user.groups for g in groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return _check
