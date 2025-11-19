# Sprint 3: Base de Datos con PostgreSQL + Alembic

## Objetivo
Implementar persistencia de datos con PostgreSQL para guardar historial de análisis de código

## ¿Qué vamos a construir?

Sistema de base de datos que:
- Guarda cada análisis realizado
- Asocia análisis con usuarios (preparado para futuro auth)
- Permite consultar historial
- Usa migraciones con Alembic
- Connection pooling con SQLAlchemy

---

## Arquitectura de Datos
```
Usuario
  ↓ POST /api/v1/analyze
  ↓
Endpoint analiza código
  ↓
Guarda en BD (analysis table)
  ↓
Retorna response + ID del análisis guardado
```

### Modelo de Datos
```sql
CREATE TABLE analysis (
    id UUID PRIMARY KEY,
    code TEXT NOT NULL,
    total_lines INTEGER NOT NULL,
    code_lines INTEGER NOT NULL,
    complexity INTEGER NOT NULL,
    num_functions INTEGER NOT NULL,
    num_classes INTEGER NOT NULL,
    num_imports INTEGER NOT NULL,
    functions_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(255)  -- Para futuro
);

CREATE INDEX idx_analysis_created_at ON analysis(created_at);
CREATE INDEX idx_analysis_user_id ON analysis(user_id);
```

---

## ARCHIVO 1: backend/pyproject.toml (ACTUALIZACIÓN)

### ¿Qué cambia?
Agregar dependencias de base de datos

### Agregar estas dependencias:
```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
    # NUEVAS DEPENDENCIAS ↓
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "psycopg2-binary>=2.9.9",  # Driver PostgreSQL
    "asyncpg>=0.29.0",  # Async driver
]
```

---

## ARCHIVO 2: backend/src/core/config.py (ACTUALIZACIÓN)

### ¿Qué cambia?
Agregar configuración de base de datos

### Agregar al Settings:
```python
class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""
    
    # Información de la API
    app_name: str = "DevSpell API"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS - URLs permitidas para acceder a la API
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # BASE DE DATOS (NUEVO) ↓
    database_url: str = "postgresql://devspell:devspell123@localhost:5432/devspell"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instancia global de configuración
settings = Settings()
```

---

## ARCHIVO 3: backend/src/core/database.py

### ¿Qué es?
Configuración de SQLAlchemy y funciones para manejo de sesiones

### Código completo:
```python
"""
Configuración de base de datos con SQLAlchemy.
"""
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import settings
from src.core.logger import logger


class Base(DeclarativeBase):
    """Clase base para todos los modelos."""
    pass


# Engine síncrono (para Alembic migrations)
sync_engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

# Session maker síncrona
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Engine asíncrono (para FastAPI)
# Convertir postgresql:// a postgresql+asyncpg://
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

# Session maker asíncrona
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos.
    
    Yields:
        Sesión de SQLAlchemy
        
    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicializa la base de datos.
    Se debe llamar al startup de la aplicación.
    """
    logger.info("🔌 Conectando a base de datos...")
    
    # Verificar conexión
    try:
        async with async_engine.begin() as conn:
            # Probar conexión
            await conn.run_sync(lambda _: None)
        logger.info("✅ Conexión a base de datos exitosa")
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        raise


async def close_db() -> None:
    """
    Cierra las conexiones de base de datos.
    Se debe llamar al shutdown de la aplicación.
    """
    logger.info("🔌 Cerrando conexiones de base de datos...")
    await async_engine.dispose()
    logger.info("✅ Conexiones cerradas")
```

### ¿Por qué este código?
- `Base`: Clase base para todos los modelos ORM
- `sync_engine`: Para migraciones (Alembic)
- `async_engine`: Para FastAPI (mejor performance)
- `get_db()`: Dependency injection para endpoints
- `init_db()`: Verificar conexión al startup
- Connection pooling: Reutiliza conexiones eficientemente

---

## ARCHIVO 4: backend/src/models/database.py

### ¿Qué es?
Modelos SQLAlchemy (tablas de la base de datos)

### Código completo:
```python
"""
Modelos de base de datos con SQLAlchemy.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Analysis(Base):
    """
    Modelo para guardar análisis de código.
    
    Attributes:
        id: UUID único del análisis
        code: Código Python analizado
        total_lines: Líneas totales
        code_lines: Líneas de código (sin comentarios)
        complexity: Complejidad ciclomática
        num_functions: Número de funciones
        num_classes: Número de clases
        num_imports: Número de imports
        functions_data: JSON con detalle de funciones
        created_at: Timestamp de creación
        user_id: ID del usuario (para futuro auth)
    """
    
    __tablename__ = "analysis"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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
    functions_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Usuario (para futuro)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        """Representación del objeto."""
        return (
            f"<Analysis(id={self.id}, "
            f"code_lines={self.code_lines}, "
            f"complexity={self.complexity})>"
        )
```

### ¿Por qué este código?
- `Mapped`: Type hints para SQLAlchemy 2.0
- `UUID`: Identificadores únicos y seguros
- `JSON`: Guardar lista de funciones como JSON
- `DateTime(timezone=True)`: Timestamps con zona horaria
- Índices se crearán en la migración de Alembic

---

## ARCHIVO 5: backend/src/models/analyze.py (ACTUALIZACIÓN)

### ¿Qué cambia?
Agregar ID del análisis guardado en la respuesta

### Actualizar AnalyzeResponse:
```python
from uuid import UUID  # Agregar este import al inicio

# ... código existente ...

class AnalyzeResponse(BaseModel):
    """Response con métricas del código analizado."""
    id: Optional[UUID] = Field(None, description="ID del análisis guardado en BD")  # NUEVO
    total_lines: int = Field(..., description="Líneas totales incluyendo vacías")
    code_lines: int = Field(..., description="Líneas de código (sin comentarios ni vacías)")
    complexity: int = Field(..., description="Complejidad ciclomática total")
    num_functions: int = Field(..., description="Número de funciones definidas")
    num_classes: int = Field(..., description="Número de clases definidas")
    num_imports: int = Field(..., description="Número de imports")
    functions: list[FunctionInfo] = Field(default_factory=list, description="Lista de funciones detectadas")
```

---

## ARCHIVO 6: backend/src/repositories/analysis_repository.py

### ¿Qué es?
Capa de acceso a datos (Repository pattern) para operaciones CRUD

### Código completo:
```python
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
        functions_data = [
            {
                "name": func.name,
                "line_start": func.line_start,
                "line_end": func.line_end,
                "complexity": func.complexity,
            }
            for func in metrics.get("functions", [])
        ]
        
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
```

### ¿Por qué este código?
- **Repository Pattern**: Separa lógica de BD de lógica de negocio
- `create()`: Guarda análisis en BD
- `get_by_id()`: Recupera análisis específico
- `get_recent()`: Lista últimos análisis
- `to_response()`: Convierte modelo de BD a Pydantic

---

## ARCHIVO 7: backend/src/api/routes/analyze.py (ACTUALIZACIÓN)

### ¿Qué cambia?
Guardar análisis en BD después de analizarlo

### Código actualizado:
```python
"""
Endpoint para análisis de código.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.analyze import AnalyzeRequest, AnalyzeResponse
from src.services.code_analyzer import analyze_code, CodeAnalysisError
from src.repositories.analysis_repository import AnalysisRepository
from src.core.database import get_db
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
    
    **Persistencia:**
    - El análisis se guarda en base de datos
    - Retorna ID único del análisis
    
    **Validaciones:**
    - El código no puede estar vacío
    - Debe ser Python sintácticamente válido
    """,
)
async def analyze_python_code(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """
    Analiza código Python y retorna métricas.
    
    Args:
        request: Código Python a analizar
        db: Sesión de base de datos
        
    Returns:
        Métricas del código con ID del análisis guardado
        
    Raises:
        HTTPException 400: Si el código tiene errores de sintaxis
        HTTPException 500: Si hay error interno al analizar
    """
    try:
        logger.info(f"Analizando código de {len(request.code)} caracteres")
        
        # Analizar código
        metrics = analyze_code(request.code)
        
        # Guardar en base de datos
        repo = AnalysisRepository(db)
        analysis = await repo.create(code=request.code, metrics=metrics)
        
        logger.info(
            f"Análisis completado y guardado: ID={analysis.id}, "
            f"{metrics['code_lines']} líneas, complejidad {metrics['complexity']}"
        )
        
        # Retornar response con ID
        response = repo.to_response(analysis)
        return response
        
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
```

---

## ARCHIVO 8: backend/src/api/routes/history.py (NUEVO)

### ¿Qué es?
Endpoint para consultar historial de análisis

### Código completo:
```python
"""
Endpoint para consultar historial de análisis.
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.analyze import AnalyzeResponse
from src.repositories.analysis_repository import AnalysisRepository
from src.core.database import get_db
from src.core.logger import logger


router = APIRouter(tags=["History"])


@router.get(
    "/history",
    response_model=list[AnalyzeResponse],
    summary="Obtener historial de análisis",
    description="Retorna los análisis más recientes guardados en base de datos.",
)
async def get_analysis_history(
    limit: int = Query(default=10, ge=1, le=100, description="Número de resultados"),
    db: AsyncSession = Depends(get_db),
) -> list[AnalyzeResponse]:
    """
    Obtiene historial de análisis.
    
    Args:
        limit: Número máximo de resultados (1-100)
        db: Sesión de base de datos
        
    Returns:
        Lista de análisis ordenados por fecha descendente
    """
    try:
        repo = AnalysisRepository(db)
        analyses = await repo.get_recent(limit=limit)
        
        logger.info(f"Consultando historial: {len(analyses)} análisis encontrados")
        
        return [repo.to_response(analysis) for analysis in analyses]
        
    except Exception as e:
        logger.error(f"Error al consultar historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al consultar historial",
        )


@router.get(
    "/history/{analysis_id}",
    response_model=AnalyzeResponse,
    summary="Obtener análisis por ID",
    description="Retorna un análisis específico por su ID único.",
)
async def get_analysis_by_id(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """
    Obtiene un análisis específico por ID.
    
    Args:
        analysis_id: UUID del análisis
        db: Sesión de base de datos
        
    Returns:
        Análisis encontrado
        
    Raises:
        HTTPException 404: Si el análisis no existe
    """
    try:
        repo = AnalysisRepository(db)
        analysis = await repo.get_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Análisis con ID {analysis_id} no encontrado",
            )
        
        logger.info(f"Análisis encontrado: ID={analysis_id}")
        
        return repo.to_response(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al consultar análisis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al consultar análisis",
        )
```

---

## ARCHIVO 9: backend/src/main.py (ACTUALIZACIÓN)

### ¿Qué cambia?
Inicializar y cerrar base de datos en el lifespan

### Código actualizado:
```python
"""
Aplicación principal de DevSpell API.
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logger import logger
from src.core.database import init_db, close_db  # NUEVO
from src.api.routes import health, analyze, history  # AGREGAR history


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Maneja el ciclo de vida de la aplicación.
    
    Args:
        app: Instancia de FastAPI
        
    Yields:
        None
    """
    # Startup
    logger.info(f"🚀 {settings.app_name} iniciando...")
    
    # Inicializar base de datos (NUEVO)
    await init_db()
    
    logger.info(f"📚 Documentación disponible en: http://{settings.host}:{settings.port}/docs")
    
    yield
    
    # Shutdown
    await close_db()  # NUEVO
    logger.info(f"👋 {settings.app_name} cerrando...")


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    
    Returns:
        Instancia de FastAPI configurada
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")
    app.include_router(history.router, prefix="/api/v1")  # NUEVO
    
    return app


# Instancia de la aplicación
app = create_app()
```

---

## ARCHIVO 10: backend/.env.example (ACTUALIZACIÓN)

### Agregar configuración de BD:
```
# Configuración de la aplicación
APP_NAME=DevSpell API
APP_VERSION=0.1.0
DEBUG=true

# Servidor
HOST=0.0.0.0
PORT=8000

# CORS - URLs permitidas
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Base de Datos (NUEVO)
DATABASE_URL=postgresql://devspell:devspell123@localhost:5432/devspell
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

---

## ARCHIVO 11: backend/alembic.ini

### ¿Qué es?
Configuración de Alembic para migraciones

### Código completo:
```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
# The path separator used here should be the separator specified by "version_path_separator" below.
# version_locations = %(here)s/bar:%(here)s/bat:alembic/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
# If this key is omitted entirely, it falls back to the legacy behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql://devspell:devspell123@localhost:5432/devspell


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

## ARCHIVO 12: backend/alembic/env.py

### ¿Qué es?
Script que Alembic usa para generar migraciones

### Código completo:
```python
"""
Alembic environment configuration.
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importar Base y modelos
from src.core.database import Base
from src.models import database  # noqa: F401 - Necesario para que Alembic detecte los modelos
from src.core.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set sqlalchemy.url from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()