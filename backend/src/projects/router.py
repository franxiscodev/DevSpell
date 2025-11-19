"""
Endpoints para gestión de proyectos.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.core.database import get_db
from src.projects.models import Project
from src.projects.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithOwner,
)

router = APIRouter(prefix="/projects", tags=["Proyectos"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """
    Crea un nuevo proyecto para el usuario actual.

    Requiere autenticación.
    """
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectResponse.model_validate(new_project)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[ProjectResponse]:
    """
    Lista todos los proyectos del usuario actual.

    Requiere autenticación.
    """
    stmt = select(Project).where(Project.owner_id ==
                                 current_user.id).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """
    Obtiene un proyecto específico por ID.

    Solo el propietario puede ver el proyecto.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProjectResponse:
    """
    Actualiza un proyecto existente.

    Solo el propietario puede actualizar el proyecto.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Actualizar solo los campos proporcionados
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    await db.commit()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """
    Elimina un proyecto.

    Solo el propietario puede eliminar el proyecto.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    await db.delete(project)
    await db.commit()
