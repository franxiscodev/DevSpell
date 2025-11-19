"""
Schemas de Pydantic para validación de datos de proyectos.
"""
from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS DE REQUEST (entrada)
# ============================================================================

class ProjectCreate(BaseModel):
    """Schema para crear un nuevo proyecto."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del proyecto",
        examples=["Mi Proyecto Backend"]
    )
    description: str | None = Field(
        default=None,
        description="Descripción opcional del proyecto",
        examples=["API REST con FastAPI y PostgreSQL"]
    )


class ProjectUpdate(BaseModel):
    """Schema para actualizar un proyecto existente."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Nuevo nombre del proyecto"
    )
    description: str | None = Field(
        default=None,
        description="Nueva descripción del proyecto"
    )


# ============================================================================
# SCHEMAS DE RESPONSE (salida)
# ============================================================================

class ProjectResponse(BaseModel):
    """Schema de respuesta con información del proyecto."""

    id: str
    name: str
    description: str | None
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectWithOwner(ProjectResponse):
    """Schema de proyecto que incluye información del owner."""

    owner_username: str = Field(
        ...,
        description="Username del propietario"
    )
