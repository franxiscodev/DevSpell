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