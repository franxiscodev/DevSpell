"""
Endpoints para historial de análisis de código.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.analysis.schemas import (
    AnalysisCompare,
    AnalysisCreate,
    AnalysisDetail,
    AnalysisResponse,
)
from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.core.database import get_db
from src.core.logger import logger
from src.models.analyze import FunctionInfo
from src.models.database import Analysis
from src.projects.models import Project

router = APIRouter(prefix="/analyses", tags=["Análisis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def save_analysis(
    analysis_data: AnalysisCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AnalysisResponse:
    """
    Guarda un análisis de código en la base de datos.

    Requiere autenticación y que el proyecto pertenezca al usuario.
    """
    # Verificar que el proyecto existe y pertenece al usuario
    stmt = select(Project).where(
        Project.id == analysis_data.project_id,
        Project.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Crear análisis
    new_analysis = Analysis(
        name=analysis_data.name,
        code=analysis_data.code,
        total_lines=analysis_data.total_lines,
        code_lines=analysis_data.code_lines,
        complexity=analysis_data.complexity,
        num_functions=analysis_data.num_functions,
        num_classes=analysis_data.num_classes,
        num_imports=analysis_data.num_imports,
        functions_data=analysis_data.functions_data,
        project_id=analysis_data.project_id,
        user_id=current_user.id
    )

    db.add(new_analysis)
    await db.commit()
    await db.refresh(new_analysis)

    logger.info(f"Análisis guardado: {new_analysis.id} para proyecto {project.name}")

    # Convertir functions_data a lista de FunctionInfo
    functions = []
    if new_analysis.functions_data:
        functions = [FunctionInfo(**func) for func in new_analysis.functions_data]

    return AnalysisResponse(
        id=new_analysis.id,
        name=new_analysis.name,
        total_lines=new_analysis.total_lines,
        code_lines=new_analysis.code_lines,
        complexity=new_analysis.complexity,
        num_functions=new_analysis.num_functions,
        num_classes=new_analysis.num_classes,
        num_imports=new_analysis.num_imports,
        functions=functions,
        project_id=new_analysis.project_id,
        user_id=new_analysis.user_id,
        created_at=new_analysis.created_at
    )


@router.get("/project/{project_id}", response_model=list[AnalysisResponse])
async def list_project_analyses(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[AnalysisResponse]:
    """
    Lista todos los análisis de un proyecto.

    Requiere autenticación y que el proyecto pertenezca al usuario.
    """
    # Verificar que el proyecto existe y pertenece al usuario
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

    # Obtener análisis del proyecto
    stmt = select(Analysis).where(
        Analysis.project_id == project_id
    ).order_by(Analysis.created_at.desc())

    result = await db.execute(stmt)
    analyses = result.scalars().all()

    # Convertir a response
    response_list = []
    for analysis in analyses:
        functions = []
        if analysis.functions_data:
            functions = [FunctionInfo(**func) for func in analysis.functions_data]

        response_list.append(AnalysisResponse(
            id=analysis.id,
            name=analysis.name,
            total_lines=analysis.total_lines,
            code_lines=analysis.code_lines,
            complexity=analysis.complexity,
            num_functions=analysis.num_functions,
            num_classes=analysis.num_classes,
            num_imports=analysis.num_imports,
            functions=functions,
            project_id=analysis.project_id,
            user_id=analysis.user_id,
            created_at=analysis.created_at
        ))

    return response_list


@router.get("/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(
    analysis_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AnalysisDetail:
    """
    Obtiene el detalle completo de un análisis incluyendo el código.

    Requiere autenticación y que el análisis pertenezca al usuario.
    """
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )

    # Convertir functions_data a lista de FunctionInfo
    functions = []
    if analysis.functions_data:
        functions = [FunctionInfo(**func) for func in analysis.functions_data]

    return AnalysisDetail(
        id=analysis.id,
        name=analysis.name,
        code=analysis.code,
        total_lines=analysis.total_lines,
        code_lines=analysis.code_lines,
        complexity=analysis.complexity,
        num_functions=analysis.num_functions,
        num_classes=analysis.num_classes,
        num_imports=analysis.num_imports,
        functions=functions,
        project_id=analysis.project_id,
        user_id=analysis.user_id,
        created_at=analysis.created_at
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """
    Elimina un análisis.

    Requiere autenticación y que el análisis pertenezca al usuario.
    """
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado"
        )

    await db.delete(analysis)
    await db.commit()

    logger.info(f"Análisis eliminado: {analysis_id}")


@router.get("/{id1}/compare/{id2}", response_model=AnalysisCompare)
async def compare_analyses(
    id1: str,
    id2: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AnalysisCompare:
    """
    Compara dos análisis y retorna las diferencias.

    Requiere autenticación y que ambos análisis pertenezcan al usuario.
    """
    # Obtener primer análisis
    stmt1 = select(Analysis).where(
        Analysis.id == id1,
        Analysis.user_id == current_user.id
    )
    result1 = await db.execute(stmt1)
    analysis1 = result1.scalar_one_or_none()

    if not analysis1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análisis {id1} no encontrado"
        )

    # Obtener segundo análisis
    stmt2 = select(Analysis).where(
        Analysis.id == id2,
        Analysis.user_id == current_user.id
    )
    result2 = await db.execute(stmt2)
    analysis2 = result2.scalar_one_or_none()

    if not analysis2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análisis {id2} no encontrado"
        )

    # Convertir a responses
    def to_response(analysis: Analysis) -> AnalysisResponse:
        functions = []
        if analysis.functions_data:
            functions = [FunctionInfo(**func) for func in analysis.functions_data]

        return AnalysisResponse(
            id=analysis.id,
            name=analysis.name,
            total_lines=analysis.total_lines,
            code_lines=analysis.code_lines,
            complexity=analysis.complexity,
            num_functions=analysis.num_functions,
            num_classes=analysis.num_classes,
            num_imports=analysis.num_imports,
            functions=functions,
            project_id=analysis.project_id,
            user_id=analysis.user_id,
            created_at=analysis.created_at
        )

    response1 = to_response(analysis1)
    response2 = to_response(analysis2)

    # Calcular diferencias
    differences = {
        "code_lines_diff": analysis2.code_lines - analysis1.code_lines,
        "complexity_diff": analysis2.complexity - analysis1.complexity,
        "num_functions_diff": analysis2.num_functions - analysis1.num_functions,
        "num_classes_diff": analysis2.num_classes - analysis1.num_classes,
        "num_imports_diff": analysis2.num_imports - analysis1.num_imports,
    }

    return AnalysisCompare(
        analysis1=response1,
        analysis2=response2,
        differences=differences
    )
