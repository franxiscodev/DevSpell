"""
Endpoints de autenticación.
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.auth.schemas import TokenResponse, UserRegister, UserResponse
from src.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.core.config import settings
from src.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """
    Registra un nuevo usuario en el sistema.

    - **email**: Email único del usuario
    - **username**: Nombre de usuario único
    - **password**: Password (mínimo 8 caracteres)

    Returns:
        Token JWT y datos del usuario creado
    """
    # Verificar si el email ya existe
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Verificar si el username ya existe
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )

    # Crear usuario
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Crear token
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": new_user.id},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """
    Inicia sesión con username/email y password.

    - **username**: Email o username del usuario
    - **password**: Password del usuario

    Returns:
        Token JWT y datos del usuario
    """
    # Buscar usuario por username o email
    stmt = select(User).where(
        (User.username == form_data.username) | (
            User.email == form_data.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Verificar usuario y password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    # Crear token
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Obtiene la información del usuario autenticado.

    Requiere token JWT válido en header: Authorization: Bearer <token>

    Returns:
        Datos del usuario actual
    """
    return UserResponse.model_validate(current_user)
