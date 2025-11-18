"""
Modelos Pydantic para el endpoint de análisis.
"""
from pydantic import BaseModel, Field, field_validator


class FunctionInfo(BaseModel):
    """Información de una función detectada."""
    name: str = Field(..., description="Nombre de la función")
    line_start: int = Field(..., description="Línea donde comienza")
    line_end: int = Field(..., description="Línea donde termina")
    complexity: int = Field(default=1, description="Complejidad ciclomática")


class AnalyzeRequest(BaseModel):
    """Request para analizar código."""
    code: str = Field(..., description="Código Python a analizar", min_length=1)

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        """Valida que el código no esté vacío después de strip."""
        if not v.strip():
            raise ValueError("El código no puede estar vacío")
        return v


class AnalyzeResponse(BaseModel):
    """Response con métricas del código analizado."""
    total_lines: int = Field(..., description="Líneas totales incluyendo vacías")
    code_lines: int = Field(..., description="Líneas de código (sin comentarios ni vacías)")
    complexity: int = Field(..., description="Complejidad ciclomática total")
    num_functions: int = Field(..., description="Número de funciones definidas")
    num_classes: int = Field(..., description="Número de clases definidas")
    num_imports: int = Field(..., description="Número de imports")
    functions: list[FunctionInfo] = Field(default_factory=list, description="Lista de funciones detectadas")
