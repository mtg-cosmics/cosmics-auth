from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    id_token: str | None = None
    refresh_token: str | None = None


class UserInfo(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    preferred_username: str | None = None
    groups: list[str] = []

    class Config:
        extra = "allow"
