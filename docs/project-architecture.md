# DevSpell - Arquitectura

## Estructura de directorios
```
devspell/
├── backend/
│   ├── src/
│   │   ├── api/          # Rutas FastAPI
│   │   ├── services/     # Lógica de negocio
│   │   ├── models/       # Modelos Pydantic
│   │   ├── ml/           # Modelos ML
│   │   └── core/         # Config, DB, utils
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   └── package.json
└── docs/
```

## Flujo de datos
```
Usuario → Frontend → API REST → Service → ML Model → Response
```

## Componentes
1. **API Layer**: FastAPI endpoints
2. **Service Layer**: Lógica de análisis
3. **ML Layer**: Procesamiento IA
4. **Data Layer**: PostgreSQL