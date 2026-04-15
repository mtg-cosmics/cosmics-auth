import secrets
from typing import Callable

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from .config import AuthSettings
from .models import TokenResponse, UserInfo


def create_auth_router(
    settings: AuthSettings,
    on_login: Callable[[UserInfo, Request], None] | None = None,
    post_login_redirect: str = "/",
) -> APIRouter:
    """
    Returns an APIRouter with /login, /callback, and /logout routes.
    Mount it on your FastAPI app:

        app.include_router(auth_router, prefix="/auth")
    """
    router = APIRouter()

    @router.get("/login")
    async def login(request: Request, next: str | None = None, redirect_uri: str | None = None):
        if next is not None and next not in settings.allowed_redirects:
            raise HTTPException(status_code=400, detail="Invalid redirect")
        if redirect_uri is not None and redirect_uri not in settings.allowed_redirects:
            raise HTTPException(status_code=400, detail="Invalid redirect_uri")
        effective_redirect_uri = redirect_uri or settings.redirect_uri
        state = secrets.token_urlsafe(16)
        request.session["oauth_state"] = state
        request.session["next"] = next or post_login_redirect
        request.session["redirect_uri"] = effective_redirect_uri
        params = {
            "response_type": "code",
            "client_id": settings.client_id,
            "redirect_uri": effective_redirect_uri,
            "scope": "openid email profile",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return RedirectResponse(f"{settings.authorization_url}?{query}")

    @router.get("/callback")
    async def callback(request: Request, code: str, state: str):
        if state != request.session.get("oauth_state"):
            raise HTTPException(status_code=400, detail="Invalid state")

        effective_redirect_uri = request.session.pop("redirect_uri", settings.redirect_uri)

        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                settings.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": effective_redirect_uri,
                    "client_id": settings.client_id,
                    "client_secret": settings.client_secret,
                },
            )
            token_resp.raise_for_status()
            tokens = TokenResponse(**token_resp.json())

            userinfo_resp = await client.get(
                settings.userinfo_url,
                headers={"Authorization": f"Bearer {tokens.access_token}"},
            )
            userinfo_resp.raise_for_status()
            user = UserInfo(**userinfo_resp.json())

        request.session["user"] = user.model_dump()
        request.session["access_token"] = tokens.access_token

        if on_login:
            on_login(user, request)

        redirect_to = request.session.pop("next", post_login_redirect)
        return RedirectResponse(redirect_to)

    @router.get("/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse(f"{settings.authentik_url}/application/o/{settings.client_id}/end-session/")

    return router
