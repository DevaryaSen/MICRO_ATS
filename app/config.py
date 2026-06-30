from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str = "dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 60

    # mail settings
    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: SecretStr
    mail_from: str
    mail_use_tls: bool
    frontend_url: str = "http://localhost:3000"

    # ImageKit settings
    imagekit_private_key: str = ""
    imagekit_url_endpoint: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()