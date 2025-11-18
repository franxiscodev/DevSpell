"""
Repositorio para operaciones de análisis en base de datos.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Analysis
from src.models.analyze import AnalyzeResponse, FunctionInfo


class AnalysisRepository:
    """Repositorio para operaciones CRUD de análisis."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa el repositorio.

        Args:
            db: Sesión de base de datos
        """
        self.db = db

    async def create(
        self,
        code: str,
        metrics: dict,
    ) -> Analysis:
        """
        Crea un nuevo análisis en la base de datos.

        Args:
            code: Código analizado
            metrics: Diccionario con métricas

        Returns:
            Análisis creado
        """
        # Convertir functions a dict para JSON
        functions_data = []
        for func in metrics.get("functions", []):
            # Puede venir como FunctionInfo o como dict
            if hasattr(func, 'name'):
                # Es un objeto FunctionInfo
                functions_data.append({
                    "name": func.name,
                    "line_start": func.line_start,
                    "line_end": func.line_end,
                    "complexity": func.complexity,
                })
            else:
                # Ya es un dict
                functions_data.append(func)

        analysis = Analysis(
            code=code,
            total_lines=metrics["total_lines"],
            code_lines=metrics["code_lines"],
            complexity=metrics["complexity"],
            num_functions=metrics["num_functions"],
            num_classes=metrics["num_classes"],
            num_imports=metrics["num_imports"],
            functions_data=functions_data,
        )

        self.db.add(analysis)
        await self.db.flush()  # Para obtener el ID generado

        return analysis

    async def get_by_id(self, analysis_id: UUID) -> Optional[Analysis]:
        """
        Obtiene un análisis por ID.

        Args:
            analysis_id: UUID del análisis

        Returns:
            Análisis o None si no existe
        """
        result = await self.db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def get_recent(self, limit: int = 10) -> list[Analysis]:
        """
        Obtiene los análisis más recientes.

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de análisis ordenados por fecha descendente
        """
        result = await self.db.execute(
            select(Analysis)
            .order_by(desc(Analysis.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def to_response(self, analysis: Analysis) -> AnalyzeResponse:
        """
        Convierte un modelo de BD a response Pydantic.

        Args:
            analysis: Modelo de base de datos

        Returns:
            Response Pydantic
        """
        # Convertir functions_data de JSON a lista de FunctionInfo
        functions = []
        if analysis.functions_data:
            functions = [
                FunctionInfo(**func_data)
                for func_data in analysis.functions_data
            ]

        return AnalyzeResponse(
            id=analysis.id,
            total_lines=analysis.total_lines,
            code_lines=analysis.code_lines,
            complexity=analysis.complexity,
            num_functions=analysis.num_functions,
            num_classes=analysis.num_classes,
            num_imports=analysis.num_imports,
            functions=functions,
        )
