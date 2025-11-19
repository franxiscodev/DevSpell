"""
Schemas de Pydantic para validación de datos de autenticación.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# SCHEMAS DE REQUEST (entrada)
# ============================================================================

class UserRegister(BaseModel):
    """Schema para registro de nuevo usuario."""

    email: EmailStr = Field(
        ...,
        description="Email del usuario",
        examples=["user@example.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (mínimo 8 caracteres)",
        examples=["SecurePass123!"]
    )


class UserLogin(BaseModel):
    """Schema para login de usuario."""

    username: str = Field(
        ...,
        description="Email o username del usuario",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        description="Password del usuario"
    )


# ============================================================================
# SCHEMAS DE RESPONSE (salida)
# ============================================================================

class UserResponse(BaseModel):
    """Schema de respuesta con información del usuario (SIN password)."""

    id: str
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema de respuesta con token JWT."""

    access_token: str = Field(
        ...,
        description="Token JWT de acceso"
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token"
    )
    user: UserResponse = Field(
        ...,
        description="Información del usuario autenticado"
    )


class TokenData(BaseModel):
    """Schema para datos extraídos del token."""

    user_id: str | None = None
