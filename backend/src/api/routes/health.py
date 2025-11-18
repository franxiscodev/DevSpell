"""
Health check endpoint.
"""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str
    version: str
    timestamp: str


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Verifica que la API esté funcionando.

    Returns:
        Estado de salud de la API
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
    )
