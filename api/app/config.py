"""Configuration lue exclusivement depuis l'environnement (12-factor)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Scalingo injecte SCALINGO_POSTGRESQL_URL ; en local on utilise DATABASE_URL.
    scalingo_postgresql_url: str = ""
    database_url: str = ""

    jwt_secret: str = "dev-only-secret-change-me"
    jwt_expire_minutes: int = 60

    # Liste d'origines séparées par des virgules.
    cors_origins: str = "http://localhost:5173"

    @property
    def sqlalchemy_url(self) -> str:
        url = self.scalingo_postgresql_url or self.database_url
        if not url:
            raise RuntimeError(
                "Aucune base configurée : définir DATABASE_URL (local) "
                "ou ajouter l'addon PostgreSQL (Scalingo)."
            )
        # postgres:// (Scalingo) -> postgresql+psycopg:// (SQLAlchemy 2 + psycopg 3)
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
