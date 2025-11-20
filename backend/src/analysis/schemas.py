"""
Schemas Pydantic para análisis guardados.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.models.analyze import FunctionInfo


class AnalysisCreate(BaseModel):
    """Schema para crear un análisis guardado."""

    name: Optional[str] = Field(
        None,
        max_length=200,
        description="Nombre opcional del análisis"
    )
    code: str = Field(
        ...,
        min_length=1,
        description="Código Python analizado"
    )
    total_lines: int = Field(..., ge=0)
    code_lines: int = Field(..., ge=0)
    complexity: int = Field(..., ge=0)
    num_functions: int = Field(..., ge=0)
    num_classes: int = Field(..., ge=0)
    num_imports: int = Field(..., ge=0)
    functions_data: Optional[list | dict] = Field(
        None,
        description="JSON con detalle de funciones"
    )
    project_id: str = Field(
        ...,
        description="ID del proyecto al que pertenece"
    )


class AnalysisResponse(BaseModel):
    """Schema para respuesta de análisis guardado."""

    id: str
    name: Optional[str] = None
    total_lines: int
    code_lines: int
    complexity: int
    num_functions: int
    num_classes: int
    num_imports: int
    functions: list[FunctionInfo] = Field(default_factory=list)
    project_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisDetail(AnalysisResponse):
    """Schema con detalle completo incluyendo código."""

    code: str


class AnalysisCompare(BaseModel):
    """Schema para comparar dos análisis."""

    analysis1: AnalysisResponse
    analysis2: AnalysisResponse
    differences: dict = Field(
        description="Diferencias entre los análisis"
    )
