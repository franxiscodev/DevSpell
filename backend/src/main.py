"""
Aplicación principal de DevSpell API.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logger import logger
from src.api.routes import health, analyze
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router
from src.analysis.router import router as analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    """
    # Startup
    logger.info(f"🚀 {settings.app_name} iniciando...")
    logger.info(
        f"📚 Documentación disponible en: http://{settings.host}:{settings.port}/docs")

    yield

    # Shutdown
    logger.info(f"👋 {settings.app_name} cerrando...")


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.

    Returns:
        Instancia de FastAPI configurada
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(analysis_router, prefix="/api/v1")

    return app


# Instancia de la aplicación
app = create_app()
