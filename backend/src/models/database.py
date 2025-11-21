"""
Modelos de base de datos con SQLAlchemy.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Analysis(Base):
    """
    Modelo para guardar análisis de código.

    Attributes:
        id: UUID único del análisis
        name: Nombre opcional del análisis
        code: Código Python analizado
        total_lines: Líneas totales
        code_lines: Líneas de código (sin comentarios)
        complexity: Complejidad ciclomática
        num_functions: Número de funciones
        num_classes: Número de clases
        num_imports: Número de imports
        functions_data: JSON con detalle de funciones
        project_id: ID del proyecto al que pertenece
        user_id: ID del usuario que creó el análisis
        created_at: Timestamp de creación
    """

    __tablename__ = "analysis"

    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # Nombre opcional del análisis
    name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
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
    functions_data: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)

    # Foreign Keys
    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="analyses",
        lazy="joined"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="analyses",
        lazy="joined"
    )

    def __repr__(self) -> str:
        """Representación del objeto."""
        return (
            f"<Analysis(id={self.id}, "
            f"name={self.name}, "
            f"code_lines={self.code_lines}, "
            f"complexity={self.complexity})>"
        )