# 🐳 Docker Setup - DevSpell

Guía completa para configurar y usar Docker con DevSpell.

---

## 📋 Prerrequisitos

- Docker Desktop instalado
- Archivo `.env` configurado (ver `.env.example`)

---

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno
```bash
# Copiar template
cp .env.example .env

# Editar con tus valores (Windows)
notepad .env

# Cambiar al menos:
# - POSTGRES_PASSWORD (contraseña segura)
```

### 2. Levantar PostgreSQL
```bash
docker-compose up -d
```

### 3. Verificar que está corriendo
```bash
docker-compose ps
```

Deberías ver:
```
NAME                STATUS
devspell-postgres   Up (healthy)
```

### 4. Aplicar migraciones
```bash
uv run alembic upgrade head
```

### 5. Levantar la aplicación
```bash
uv run uvicorn src.main:app --reload
```

Visita: http://localhost:8000/docs

---

## 🔧 Comandos Útiles

### Ver logs
```bash
# Logs en tiempo real
docker-compose logs -f

# Solo PostgreSQL
docker-compose logs -f postgres

# Últimas 100 líneas
docker-compose logs --tail=100
```

### Detener servicios
```bash
# Detener (mantiene datos)
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BD)
docker-compose down -v
```

### Reiniciar servicios
```bash
docker-compose restart
```

### Acceder a PostgreSQL
```bash
# Con psql desde Docker
docker exec -it devspell-postgres psql -U devspell -d devspell

# Comandos útiles dentro de psql:
# \l          - Listar bases de datos
# \dt         - Listar tablas
# \d tabla    - Describir tabla
# \q          - Salir
```

### Ver información del contenedor
```bash
# Inspeccionar contenedor
docker inspect devspell-postgres

# Ver salud del contenedor (Windows PowerShell)
docker inspect devspell-postgres | Select-String "Health" -Context 5
```

---

## 🗄️ Gestión de Base de Datos

### Backup
```bash
# Backup de la BD
docker exec devspell-postgres pg_dump -U devspell devspell > backup.sql

# Backup con fecha (PowerShell)
$date = Get-Date -Format "yyyyMMdd_HHmmss"
docker exec devspell-postgres pg_dump -U devspell devspell > "backup_$date.sql"
```

### Restore
```bash
# Restaurar desde backup
docker exec -i devspell-postgres psql -U devspell -d devspell < backup.sql
```

### Resetear base de datos
```bash
# 1. Detener y eliminar volumen
docker-compose down -v

# 2. Levantar de nuevo
docker-compose up -d

# 3. Aplicar migraciones
uv run alembic upgrade head
```

---

## 🔍 Troubleshooting

### Puerto 5433 ya en uso
```bash
# Ver qué está usando el puerto (Windows)
netstat -ano | findstr :5433

# Cambiar puerto en .env
POSTGRES_PORT=5434

# Actualizar también DATABASE_URL
DATABASE_URL=postgresql://devspell:tu_password@localhost:5434/devspell

# Reiniciar
docker-compose down
docker-compose up -d
```

### Contenedor no inicia
```bash
# Ver logs completos
docker-compose logs postgres

# Ver estado del contenedor
docker ps -a | findstr devspell-postgres

# Eliminar y recrear
docker-compose down
docker-compose up -d --force-recreate
```

### Error de conexión desde la app

Verifica que:
1. ✅ PostgreSQL está `healthy`: `docker-compose ps`
2. ✅ Puerto correcto en `DATABASE_URL` de `.env`
3. ✅ Contraseña coincide entre `POSTGRES_PASSWORD` y `DATABASE_URL`
```bash
# Probar conexión manualmente
docker exec devspell-postgres psql -U devspell -d devspell -c "SELECT 1;"
```

### Error "required variable POSTGRES_PASSWORD is missing"

El archivo `.env` no está en el directorio donde ejecutas `docker-compose`:
```bash
# Asegurarse de estar en backend/
cd C:\proyectos\devspell\backend

# Verificar que .env existe
dir .env

# O especificar el archivo explícitamente
docker-compose --env-file .env up -d
```

---

## 🔐 Seguridad

### ⚠️ NUNCA hacer:

- ❌ Subir archivo `.env` a Git
- ❌ Usar contraseñas por defecto en producción
- ❌ Exponer puerto de PostgreSQL públicamente
- ❌ Compartir credenciales en código

### ✅ SIEMPRE hacer:

- ✅ Usar `.env.example` como template
- ✅ Contraseñas fuertes y únicas
- ✅ Rotar credenciales regularmente
- ✅ Usar GitHub Secrets en CI/CD

### Generar contraseña segura
```bash
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# O más simple
[System.Web.Security.Membership]::GeneratePassword(32, 8)
```

---

## 📊 Monitoreo

### Ver uso de recursos
```bash
# Estadísticas en tiempo real
docker stats devspell-postgres

# Una sola vez
docker stats devspell-postgres --no-stream
```

### Ver tamaño de volúmenes
```bash
docker system df -v
```

---

## 🧹 Limpieza

### Limpiar recursos no usados
```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar volúmenes no usados
docker volume prune

# Limpiar todo (⚠️ CUIDADO)
docker system prune -a --volumes
```

---

## 🚀 Producción

Para producción, considera:

1. **Variables de entorno desde secrets** (no archivos .env)
2. **Backups automáticos** programados
3. **Monitoreo** con Prometheus/Grafana
4. **Alta disponibilidad** con réplicas
5. **SSL/TLS** para conexiones
6. **Límites de recursos** en docker-compose

Ver documentación de deployment para más información (próximo sprint).

---

## 📚 Recursos

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)