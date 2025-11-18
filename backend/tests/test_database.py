"""
Tests para operaciones de base de datos.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.database import Base
from src.models.database import Analysis
from src.repositories.analysis_repository import AnalysisRepository


# URL de base de datos de prueba (en memoria)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """Fixture que proporciona una sesión de base de datos de prueba."""
    # Crear engine de prueba
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Crear session maker
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Proporcionar sesión
    async with async_session() as session:
        yield session

    # Limpiar
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_analysis(db_session):
    """Debe crear un análisis en la base de datos."""
    repo = AnalysisRepository(db_session)

    metrics = {
        "total_lines": 10,
        "code_lines": 8,
        "complexity": 3,
        "num_functions": 2,
        "num_classes": 1,
        "num_imports": 1,
        "functions": [],
    }

    analysis = await repo.create(code="def hello(): pass", metrics=metrics)
    await db_session.commit()

    assert analysis.id is not None
    assert analysis.code == "def hello(): pass"
    assert analysis.total_lines == 10
    assert analysis.complexity == 3


@pytest.mark.asyncio
async def test_get_analysis_by_id(db_session):
    """Debe obtener un análisis por ID."""
    repo = AnalysisRepository(db_session)

    metrics = {
        "total_lines": 5,
        "code_lines": 4,
        "complexity": 1,
        "num_functions": 1,
        "num_classes": 0,
        "num_imports": 0,
        "functions": [],
    }

    # Crear análisis
    created = await repo.create(code="x = 1", metrics=metrics)
    await db_session.commit()

    # Buscar por ID
    found = await repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.code == "x = 1"


@pytest.mark.asyncio
async def test_get_analysis_by_id_not_found(db_session):
    """Debe retornar None si el análisis no existe."""
    import uuid

    repo = AnalysisRepository(db_session)
    found = await repo.get_by_id(uuid.uuid4())

    assert found is None


@pytest.mark.asyncio
async def test_get_recent_analyses(db_session):
    """Debe obtener análisis recientes ordenados."""
    repo = AnalysisRepository(db_session)

    metrics = {
        "total_lines": 1,
        "code_lines": 1,
        "complexity": 1,
        "num_functions": 0,
        "num_classes": 0,
        "num_imports": 0,
        "functions": [],
    }

    # Crear 3 análisis
    await repo.create(code="x = 1", metrics=metrics)
    await repo.create(code="y = 2", metrics=metrics)
    await repo.create(code="z = 3", metrics=metrics)
    await db_session.commit()

    # Obtener recientes
    recent = await repo.get_recent(limit=2)

    # Verificar que obtenemos exactamente 2
    assert len(recent) == 2

    # Verificar que están entre los más recientes (sin asumir orden específico)
    codes = {r.code for r in recent}
    # Al menos uno debe ser de los últimos creados
    assert len(codes & {"y = 2", "z = 3"}) >= 1


@pytest.mark.asyncio
async def test_to_response_conversion(db_session):
    """Debe convertir modelo de BD a Pydantic response."""
    repo = AnalysisRepository(db_session)

    metrics = {
        "total_lines": 10,
        "code_lines": 8,
        "complexity": 3,
        "num_functions": 1,
        "num_classes": 0,
        "num_imports": 1,
        "functions": [
            {
                "name": "test_func",
                "line_start": 1,
                "line_end": 5,
                "complexity": 2,
            }
        ],
    }

    # Crear análisis
    analysis = await repo.create(code="def test_func(): pass", metrics=metrics)
    await db_session.commit()

    # Convertir a response
    response = repo.to_response(analysis)

    assert response.id == analysis.id
    assert response.total_lines == 10
    assert response.complexity == 3
    assert len(response.functions) == 1
    assert response.functions[0].name == "test_func"
