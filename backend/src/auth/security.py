"""
Utilidades de seguridad para autenticación.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings

# Configuración de hashing con argon2 (más moderno que bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que un password en texto plano coincida con el hash.

    Args:
        plain_password: Password en texto plano
        hashed_password: Password hasheado

    Returns:
        True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro del password usando argon2.

    Args:
        password: Password en texto plano

    Returns:
        Password hasheado con argon2
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        data: Datos a incluir en el token (normalmente {"sub": user_id})
        expires_delta: Tiempo de expiración personalizado

    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decodifica y verifica un token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.JWTError:
        return None
