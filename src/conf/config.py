from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    MAIL_USERNAME: EmailStr = "<EMAIL>"
    MAIL_PASSWORD: str = "<PASSWORD>"
    MAIL_FROM: EmailStr = "email@example.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Gmail"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = "<CLD_NAME>"
    CLD_API_KEY: int = "<CLD_API_KEY>"
    CLD_API_SECRET: str = "<CLD_API_SECRET>"

    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
