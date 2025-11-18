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
        "http://localhost:3000", "http://localhost:5173"]

    # BASE DE DATOS
    database_url: str = "postgresql://devspell:devspell123@localhost:5433/devspell"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # POSTGRES (variables para Docker)
    postgres_user: str = "devspell"
    postgres_password: str = "devspell123"
    postgres_db: str = "devspell"
    postgres_port: int = 5433

    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instancia global de configuración
settings = Settings()
