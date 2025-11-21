"""
Rutas de API para servicios de IA.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.services.ai import get_ai_provider
from src.core.logger import logger

router = APIRouter(prefix="/ai", tags=["AI"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SuggestionsRequest(BaseModel):
    """Request para obtener sugerencias de mejora."""
    code: str
    analysis: Dict[str, Any]  # Resultados del análisis (complexity, num_functions, etc.)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
                "analysis": {
                    "complexity": 2,
                    "num_functions": 1,
                    "code_lines": 3
                }
            }
        }


class SuggestionsResponse(BaseModel):
    """Response con sugerencias de mejora."""
    suggestions: List[str]


class ExplainRequest(BaseModel):
    """Request para explicar una función."""
    function_name: str
    function_code: str

    class Config:
        json_schema_extra = {
            "example": {
                "function_name": "factorial",
                "function_code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)"
            }
        }


class ExplainResponse(BaseModel):
    """Response con explicación de la función."""
    explanation: str


class OptimizeRequest(BaseModel):
    """Request para optimizar código."""
    code: str

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def sum_list(numbers):\n    total = 0\n    for num in numbers:\n        total = total + num\n    return total"
            }
        }


class OptimizeResponse(BaseModel):
    """Response con código optimizado."""
    optimized_code: str


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_code_suggestions(
    request: SuggestionsRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtener sugerencias de mejora para código analizado.

    Requiere autenticación JWT.

    Returns:
        Lista de sugerencias concretas para mejorar el código
    """
    try:
        logger.info(f"[AI] User {current_user.username} requesting suggestions for {len(request.code)} chars of code")

        provider = get_ai_provider()
        suggestions = await provider.generate_suggestions(request.code, request.analysis)

        logger.info(f"[AI] Generated {len(suggestions)} suggestions")
        return SuggestionsResponse(suggestions=suggestions)

    except Exception as e:
        logger.error(f"[AI] Error generating suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating suggestions: {str(e)}"
        )


@router.post("/explain", response_model=ExplainResponse)
async def explain_function(
    request: ExplainRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Explicar qué hace una función específica.

    Requiere autenticación JWT.

    Returns:
        Explicación detallada de la función
    """
    try:
        logger.info(f"[AI] User {current_user.username} requesting explanation for function '{request.function_name}'")

        provider = get_ai_provider()
        explanation = await provider.explain_function(
            request.function_code,
            request.function_name
        )

        logger.info(f"[AI] Generated explanation ({len(explanation)} chars)")
        return ExplainResponse(explanation=explanation)

    except Exception as e:
        logger.error(f"[AI] Error explaining function: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating explanation: {str(e)}"
        )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_code(
    request: OptimizeRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Optimizar código reduciendo complejidad.

    Requiere autenticación JWT.

    Returns:
        Versión optimizada del código con explicaciones
    """
    try:
        logger.info(f"[AI] User {current_user.username} requesting code optimization for {len(request.code)} chars")

        provider = get_ai_provider()
        optimized = await provider.optimize_code(request.code)

        logger.info(f"[AI] Generated optimized code ({len(optimized)} chars)")
        return OptimizeResponse(optimized_code=optimized)

    except Exception as e:
        logger.error(f"[AI] Error optimizing code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating optimization: {str(e)}"
        )
