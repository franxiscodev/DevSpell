"""
Configuración central de la aplicación DevSpell.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # Información de la API
    app_name: str = "DevSpell API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS - URLs permitidas para acceder a la API
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    # PostgreSQL - Campos individuales
    postgres_user: str = "devspell"
    postgres_password: str = "devspell_local_2024"
    postgres_host: str = "localhost"
    postgres_port: str = "5433"
    postgres_db: str = "devspell"

    # Database pool
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Anthropic API
    anthropic_api_key: str = ""

    # Autenticación JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión a PostgreSQL para asyncpg."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """URL de conexión síncrona para Alembic (psycopg2)."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Permite campos extra del .env sin error
    )


# Instancia global de configuración
settings = Settings()
