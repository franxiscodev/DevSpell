#!/bin/bash
# =============================================================================
# DevSpell - PostgreSQL Initialization Script
# =============================================================================

set -e

echo "🔧 Inicializando base de datos DevSpell..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Extensiones útiles
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Configuración
    ALTER DATABASE $POSTGRES_DB SET timezone TO 'UTC';
    
    -- Log
    SELECT '✅ Base de datos DevSpell inicializada correctamente' AS status;
EOSQL

echo "✅ Script de inicialización completado"