"""
Modelos de base de datos para proyectos.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Project(Base):
    """
    Modelo de proyecto en la base de datos.

    Un proyecto pertenece a un usuario y puede contener múltiples análisis.

    Attributes:
        id: UUID único del proyecto
        name: Nombre del proyecto
        description: Descripción opcional del proyecto
        owner_id: ID del usuario propietario
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    owner_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
        lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Project {self.name} (owner: {self.owner_id})>"
