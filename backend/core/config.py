from pydantic_settings import BaseSettings
from sqlalchemy.orm import DeclarativeBase


class Settings(BaseSettings):
    """Application settings"""
    DEBUG: bool = True
    DB_URL_DEV: str = "sqlite+aiosqlite:///./ragnarokcs.db"
    DB_URL_PROD: str
    algorith: str = "HS256"
    acess_token_expire_minutes: int = 60
    API_V1_STR: str = "/api/v1"

    @property
    def db_url(self) -> str:
        """Return the appropriate database URL based on the environment"""
        return self.DB_URL_DEV if self.DEBUG else self.DB_URL_PROD

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()  # noqa


class DBBaseModel(DeclarativeBase):
    """Base model for all database models"""
    pass
