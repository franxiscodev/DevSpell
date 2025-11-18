\# Especificación: Backend Base Setup



\## Objetivo

Crear estructura inicial del backend FastAPI con configuración profesional.



\## Estructura de directorios esperada

```

backend/

├── src/

│   ├── \_\_init\_\_.py

│   ├── main.py              # Aplicación FastAPI principal

│   ├── core/

│   │   ├── \_\_init\_\_.py

│   │   ├── config.py        # Pydantic Settings

│   │   ├── logging.py       # Logger estructurado

│   │   └── middleware.py    # CORS y otros middleware

│   └── api/

│       ├── \_\_init\_\_.py

│       └── routes/

│           ├── \_\_init\_\_.py

│           └── health.py    # Health check endpoint

├── tests/

│   ├── \_\_init\_\_.py

│   └── test\_health.py

├── pyproject.toml           # Configuración uv

└── .env.example             # Variables de entorno ejemplo

```



\## Requisitos Técnicos



\### 1. Dependencias (pyproject.toml)

```toml

\[project]

name = "devspell-backend"

version = "0.1.0"

requires-python = ">=3.11"

dependencies = \[

&nbsp;   "fastapi>=0.104.0",

&nbsp;   "uvicorn\[standard]>=0.24.0",

&nbsp;   "pydantic>=2.5.0",

&nbsp;   "pydantic-settings>=2.1.0",

&nbsp;   "python-dotenv>=1.0.0",

]



\[project.optional-dependencies]

dev = \[

&nbsp;   "pytest>=7.4.0",

&nbsp;   "pytest-asyncio>=0.21.0",

&nbsp;   "httpx>=0.25.0",

&nbsp;   "ruff>=0.1.0",

]



\[tool.ruff]

line-length = 100

target-version = "py311"

```



\### 2. Configuración (core/config.py)

\*\*Inputs:\*\* Variables de entorno

\*\*Output:\*\* Objeto Settings singleton

\*\*Validaciones:\*\*

\- PORT debe estar entre 1000-9999

\- LOG\_LEVEL debe ser válido (DEBUG, INFO, WARNING, ERROR)

\- Environment debe ser "development" o "production"



\*\*Campos requeridos:\*\*

```python

PROJECT\_NAME: str = "DevSpell"

VERSION: str = "0.1.0"

ENVIRONMENT: str = "development"

DEBUG: bool = True

PORT: int = 8000

LOG\_LEVEL: str = "INFO"

CORS\_ORIGINS: list\[str] = \["http://localhost:3000"]

```



\### 3. Logger (core/logging.py)

\*\*Output:\*\* Logger configurado con formato JSON estructurado

\*\*Campos en logs:\*\*

\- timestamp

\- level

\- message

\- module

\- function



\### 4. Aplicación FastAPI (main.py)

\*\*Características:\*\*

\- Título y versión desde config

\- CORS middleware configurado

\- Logging de requests/responses

\- Incluir router de health

\- Docs en /docs y /redoc



\### 5. Health Check Endpoint (api/routes/health.py)

\*\*Ruta:\*\* GET /health

\*\*Response:\*\*

```json

{

&nbsp; "status": "healthy",

&nbsp; "version": "0.1.0",

&nbsp; "environment": "development"

}

```



\### 6. Tests (tests/test\_health.py)

\*\*Casos:\*\*

\- Test status code 200

\- Test response structure

\- Test campos requeridos



\## Estándares a Seguir

\- ✅ Type hints en todas las funciones

\- ✅ Docstrings formato Google Style

\- ✅ snake\_case para variables/funciones

\- ✅ PascalCase para clases

\- ✅ Manejo explícito de errores

\- ✅ f-strings para formateo



\## Comandos de Validación

```bash

\# Instalar dependencias

cd backend \&\& uv sync



\# Ejecutar tests

uv run pytest



\# Linter

uv run ruff check src/



\# Ejecutar servidor

uv run uvicorn src.main:app --reload --port 8000

```



\## Criterios de Éxito

1\. ✅ Servidor levanta en http://localhost:8000

2\. ✅ GET /health retorna status 200

3\. ✅ Docs accesibles en /docs

4\. ✅ Tests pasan con 100% coverage en health endpoint

5\. ✅ Ruff no reporta errores

