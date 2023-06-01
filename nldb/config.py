from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    database: str = "nldb.db"
    openai_api_key: str = None
    uvicorn_host: str = "0.0.0.0"  # noqa: S104
    uvicorn_port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
