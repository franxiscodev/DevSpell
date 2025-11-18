"""
Modelos de base de datos con SQLAlchemy.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Analysis(Base):
    """
    Modelo para guardar análisis de código.
    
    Attributes:
        id: UUID único del análisis
        code: Código Python analizado
        total_lines: Líneas totales
        code_lines: Líneas de código (sin comentarios)
        complexity: Complejidad ciclomática
        num_functions: Número de funciones
        num_classes: Número de clases
        num_imports: Número de imports
        functions_data: JSON con detalle de funciones
        created_at: Timestamp de creación
        user_id: ID del usuario (para futuro auth)
    """
    
    __tablename__ = "analysis"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Código analizado
    code: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Métricas
    total_lines: Mapped[int] = mapped_column(Integer, nullable=False)
    code_lines: Mapped[int] = mapped_column(Integer, nullable=False)
    complexity: Mapped[int] = mapped_column(Integer, nullable=False)
    num_functions: Mapped[int] = mapped_column(Integer, nullable=False)
    num_classes: Mapped[int] = mapped_column(Integer, nullable=False)
    num_imports: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Datos de funciones (JSON)
    functions_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Usuario (para futuro)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        """Representación del objeto."""
        return (
            f"<Analysis(id={self.id}, "
            f"code_lines={self.code_lines}, "
            f"complexity={self.complexity})>"
        )