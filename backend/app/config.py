from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:sujanix%23123@localhost:5432/ai-crm-hcp-module"
    GROQ_API_KEY: str = ""  # Set via GROQ_API_KEY in backend/.env
    DEFAULT_MODEL: str = "gemma2-9b-it"
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
