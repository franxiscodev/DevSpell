"""
Endpoint para análisis de código.
"""
from fastapi import APIRouter, HTTPException, status

from src.models.analyze import AnalyzeRequest, AnalyzeResponse
from src.services.code_analyzer import analyze_code, CodeAnalysisError
from src.core.logger import logger


router = APIRouter(tags=["Analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analizar código Python",
    description="""
    Analiza código Python y retorna métricas de calidad.

    **Métricas calculadas:**
    - Líneas totales y líneas de código
    - Complejidad ciclomática (McCabe)
    - Número de funciones, clases e imports
    - Detalle de cada función con su complejidad

    **Validaciones:**
    - El código no puede estar vacío
    - Debe ser Python sintácticamente válido
    """,
)
async def analyze_python_code(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analiza código Python y retorna métricas.

    Args:
        request: Código Python a analizar

    Returns:
        Métricas del código

    Raises:
        HTTPException 400: Si el código tiene errores de sintaxis
        HTTPException 500: Si hay error interno al analizar
    """
    try:
        logger.info(f"Analizando código de {len(request.code)} caracteres")

        # Analizar código
        metrics = analyze_code(request.code)

        logger.info(
            f"Análisis completado: {metrics['code_lines']} líneas, "
            f"complejidad {metrics['complexity']}"
        )

        return AnalyzeResponse(**metrics)

    except CodeAnalysisError as e:
        logger.error(f"Error al analizar código: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error inesperado al analizar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al analizar el código",
        )
