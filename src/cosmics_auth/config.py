from pydantic import field_validator
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    authentik_url: str  # e.g. https://auth.cosmics.me
    client_id: str
    client_secret: str
    redirect_uri: str  # e.g. https://myapp.cosmics.me/auth/callback
    allowed_redirects: set[str] = set()  # e.g. AUTH_ALLOWED_REDIRECTS=https://myapp.cosmics.me,http://localhost:5173

    @field_validator("allowed_redirects", mode="before")
    @classmethod
    def parse_allowed_redirects(cls, v: object) -> set[str]:
        if isinstance(v, str):
            return {u.strip() for u in v.split(",") if u.strip()}
        return set(v) if v else set()

    # Derived — override only if your Authentik slug differs
    @property
    def oidc_discovery_url(self) -> str:
        return f"{self.authentik_url}/application/o/{self.client_id}/.well-known/openid-configuration"

    @property
    def authorization_url(self) -> str:
        return f"{self.authentik_url}/application/o/authorize/"

    @property
    def token_url(self) -> str:
        return f"{self.authentik_url}/application/o/token/"

    @property
    def userinfo_url(self) -> str:
        return f"{self.authentik_url}/application/o/userinfo/"

    @property
    def jwks_url(self) -> str:
        return f"{self.authentik_url}/application/o/{self.client_id}/jwks/"

    class Config:
        env_prefix = "AUTH_"
        env_file = ".env"
