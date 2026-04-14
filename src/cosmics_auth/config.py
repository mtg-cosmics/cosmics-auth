from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    authentik_url: str  # e.g. https://auth.cosmics.me
    client_id: str
    client_secret: str
    redirect_uri: str  # e.g. https://myapp.cosmics.me/auth/callback

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
