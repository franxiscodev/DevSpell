# Sprint 1: Backend Base Setup

## Objetivo
Crear la estructura base de FastAPI funcional con configuración profesional

## ¿Por qué este orden?
1. Primero configuramos el proyecto (pyproject.toml)
2. Luego la configuración de la app (config.py)
3. Después utilidades (logger.py)
4. Luego endpoints simples (health.py)
5. Finalmente la app principal (main.py)
6. Y tests para validar

---

## ARCHIVO 1: backend/pyproject.toml

### ¿Qué es?
Archivo de configuración del proyecto Python. Define:
- Nombre del proyecto
- Versión de Python requerida
- Dependencias (librerías que necesitamos)
- Herramientas de desarrollo

### Contenido exacto:
```toml
[project]
name = "devspell-backend"
version = "0.1.0"
description = "DevSpell Backend - Análisis de código con IA"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 88
target-version = "py311"
```

### ¿Para qué sirve cada dependencia?
- `fastapi`: Framework web para crear APIs
- `uvicorn`: Servidor para correr FastAPI
- `pydantic`: Validación de datos
- `pydantic-settings`: Configuración desde variables de entorno
- `python-dotenv`: Leer archivos .env
- `pytest`: Framework de testing
- `httpx`: Cliente HTTP para tests
- `ruff`: Linter para validar código

---

## ARCHIVO 2: backend/src/core/config.py

### ¿Qué es?
Configuración centralizada de la aplicación. Aquí definimos:
- Nombre de la app
- Puerto donde corre
- URLs permitidas (CORS)
- Si estamos en modo desarrollo o producción

### Estructura requerida:
```python
"""
Configuración central de la aplicación DevSpell.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    
    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instancia global de configuración
settings = Settings()
```

### ¿Por qué este código?
- `BaseSettings`: Lee variables del archivo .env automáticamente
- `app_name`, `app_version`: Información que aparecerá en /docs
- `cors_origins`: Lista de URLs que pueden hacer peticiones a nuestra API
- `settings = Settings()`: Creamos una instancia que usaremos en toda la app

---

## ARCHIVO 3: backend/src/core/logger.py

### ¿Qué es?
Sistema de logging para registrar lo que pasa en la aplicación.

### Estructura requerida:
```python
"""
Sistema de logging estructurado para DevSpell.
"""
import logging
import sys
from typing import Any


def setup_logger(name: str = "devspell") -> logging.Logger:
    """
    Configura y retorna un logger.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Handler para consola
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Logger global
logger = setup_logger()
```

### ¿Por qué este código?
- Registra eventos en formato legible
- Muestra fecha, hora, nivel (INFO, ERROR, etc.)
- Se puede usar en toda la aplicación

---

## ARCHIVO 4: backend/src/api/routes/health.py

### ¿Qué es?
Endpoint simple que indica si la API está funcionando.

### Estructura requerida:
```python
"""
Health check endpoint.
"""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str
    version: str
    timestamp: str


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Verifica que la API esté funcionando.
    
    Returns:
        Estado de salud de la API
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
    )
```

### ¿Por qué este código?
- `APIRouter`: Agrupa endpoints relacionados
- `HealthResponse`: Define la estructura de la respuesta
- `response_model`: FastAPI valida que la respuesta tenga este formato
- Retorna: status (estado), version, timestamp (fecha/hora actual)

---

## ARCHIVO 5: backend/src/main.py

### ¿Qué es?
Aplicación principal de FastAPI. Aquí se configura todo.

### Estructura requerida:
```python
"""
Aplicación principal de DevSpell API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logger import logger
from src.api.routes import health


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
    
    # Event handlers
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"🚀 {settings.app_name} iniciando...")
        logger.info(f"📚 Documentación disponible en: http://{settings.host}:{settings.port}/docs")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"👋 {settings.app_name} cerrando...")
    
    return app


# Instancia de la aplicación
app = create_app()
```

### ¿Por qué este código?
- `create_app()`: Función que crea la app (útil para tests)
- `CORSMiddleware`: Permite que el frontend acceda a la API
- `include_router`: Conecta el health endpoint
- `on_event`: Funciones que se ejecutan al iniciar/cerrar

---

## ARCHIVO 6: backend/.env.example

### ¿Qué es?
Template de variables de entorno. No contiene datos sensibles.

### Contenido exacto:
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
```

### ¿Por qué este archivo?
- Muestra qué variables se pueden configurar
- No se sube a Git con datos reales
- Cada desarrollador copia este archivo a `.env` con sus valores

---

## ARCHIVO 7: backend/tests/test_health.py

### ¿Qué es?
Tests automatizados para el health endpoint.

### Estructura requerida:
```python
"""
Tests para el health endpoint.
"""
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_health_endpoint_returns_200():
    """El endpoint debe retornar status code 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_structure():
    """El endpoint debe retornar la estructura correcta."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data


def test_health_status_is_healthy():
    """El status debe ser 'healthy'."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    assert data["status"] == "healthy"
```

### ¿Por qué estos tests?
- `test_*`: Pytest detecta automáticamente funciones que empiezan con test_
- `TestClient`: Simula peticiones HTTP sin levantar servidor
- `assert`: Verifica que algo sea verdadero

---

## Orden de Creación

1. ✅ pyproject.toml (configuración del proyecto)
2. ✅ src/core/config.py (configuración de la app)
3. ✅ src/core/logger.py (sistema de logs)
4. ✅ src/api/routes/health.py (endpoint simple)
5. ✅ src/main.py (app principal)
6. ✅ .env.example (template de variables)
7. ✅ tests/test_health.py (tests)

## Validación Final

Al terminar, debes poder:
- ✅ Ejecutar: `uv run uvicorn src.main:app --reload`
- ✅ Ver: http://localhost:8000/docs (documentación Swagger)
- ✅ Probar: http://localhost:8000/api/v1/health
- ✅ Tests: `uv run pytest tests/ -v` (todos pasan)