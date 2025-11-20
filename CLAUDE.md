# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevSpell is a Python code static analysis system with AI integration. It's a monorepo with:
- **Backend**: FastAPI REST API with PostgreSQL, JWT authentication, and code analysis engine
- **Frontend**: Next.js 16 (App Router) with TypeScript and TailwindCSS
- **Purpose**: Educational project to master Claude Code while building a production-grade code analyzer

## Architecture

### Backend Architecture (Clean Architecture + Repository Pattern)

```
src/
├── api/routes/          # REST endpoints (health, analyze)
├── auth/                # JWT authentication, User model, security utilities
├── projects/            # Projects CRUD, ownership validation
├── services/            # Business logic (CodeAnalyzer, AST visitor)
├── repositories/        # Data access layer
├── models/              # Pydantic schemas and SQLAlchemy models
└── core/                # Config, database, logging
```

**Key architectural decisions**:
- **Async-first**: All database operations use SQLAlchemy async with asyncpg
- **Dependency injection**: FastAPI's `Depends()` for database sessions and auth
- **Two database URLs**: `database_url` (asyncpg) for app, `sync_database_url` (psycopg2) for Alembic migrations
- **Settings pattern**: Single `Settings` class (Pydantic) constructs DB URLs from individual components
- **JWT storage**: Tokens stored in localStorage (frontend), validated via Authorization header

### Frontend Architecture (Next.js App Router)

```
app/
├── login/              # Authentication page with LoginForm component
├── register/           # User registration with RegisterForm component
├── dashboard/          # Protected dashboard (checks auth on mount)
└── page.tsx            # Landing page (placeholder)

lib/api/
├── client.ts           # ApiClient class with automatic auth headers
├── auth.ts             # authApi (login, register, getMe, logout)
└── projects.ts         # projectsApi (CRUD operations)
```

**Key patterns**:
- Client components (`'use client'`) for interactivity
- API client centralizes auth header injection
- Auth check via `useEffect` in protected routes
- localStorage for token and user data persistence

### Database Schema

- **users**: id (UUID), email, username, hashed_password (Argon2), is_active, is_superuser, timestamps
- **projects**: id (UUID), name, description, owner_id (FK to users), timestamps
- **Relationship**: User → Projects (one-to-many, CASCADE delete)

## Development Commands

### First-Time Setup

1. **Backend setup**:
```bash
cd backend

# Copy and configure environment
cp .env.example .env
# Edit .env: Set POSTGRES_PASSWORD and SECRET_KEY
# Generate SECRET_KEY with: uv run python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start PostgreSQL
docker-compose up -d

# Install dependencies (uses uv, not pip)
uv sync

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Frontend setup**:
```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional, defaults work)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start dev server
npm run dev
```

### Daily Development Workflow

**Backend**:
```bash
cd backend

# Start/stop database
docker-compose up -d        # Start PostgreSQL
docker-compose down         # Stop (data persists)
docker-compose down -v      # Stop and delete data

# Run API server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest                           # All tests
uv run pytest tests/test_analyzer.py    # Single file
uv run pytest -v -s                     # Verbose with print output
uv run pytest -k "test_name"            # Run specific test

# Database migrations
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                              # Apply migrations
uv run alembic downgrade -1                              # Rollback one
uv run alembic history                                   # View history
uv run alembic current                                   # Current version

# Linting
uv run ruff check .         # Check
uv run ruff check --fix .   # Auto-fix
```

**Frontend**:
```bash
cd frontend

npm run dev     # Dev server (http://localhost:3000)
npm run build   # Production build
npm run start   # Production server
npm run lint    # ESLint
```

### Key URLs

- **Backend API**: http://localhost:8000
- **Swagger docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5433 (custom port to avoid conflicts)

### Common Development Tasks

**Add a new authenticated endpoint**:
1. Create router in `backend/src/<module>/router.py`
2. Use `get_current_active_user` dependency for auth
3. Include router in `src/main.py` with `/api/v1` prefix
4. Add corresponding service in `frontend/lib/api/`

**Create a database migration**:
1. Modify SQLAlchemy models in `backend/src/<module>/models.py`
2. Run `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration in `backend/alembic/versions/`
4. Apply with `uv run alembic upgrade head`

**Add a new API endpoint to frontend**:
1. Define TypeScript types in `frontend/types/index.ts`
2. Add method to appropriate service in `frontend/lib/api/`
3. Use `ApiClient` for automatic auth headers

## Project Conventions

### Backend
- **Python version**: 3.11+ (uses modern type hints with `|` syntax)
- **Package manager**: `uv` (NOT pip) - much faster, handles dependency groups
- **Code style**: Ruff with line length 88, auto-format on save recommended
- **Async patterns**: Always use `async def` for routes and DB operations
- **Password hashing**: Argon2-CFFI (via passlib) - winner of Password Hashing Competition
- **Database sessions**: Always use `get_db()` dependency, never create sessions manually
- **Error handling**: Raise HTTPException with appropriate status codes
- **Logging**: Use `logger` from `src.core.logger`, not `print()`

### Frontend
- **TypeScript**: Strict mode enabled, always define types for API responses
- **Component pattern**: Extract forms into separate components in `components/`
- **API calls**: Always use `authApi` or service classes from `lib/api/`, never raw fetch
- **Auth pattern**: Store token in localStorage, check on protected route mount
- **Styling**: TailwindCSS utility classes, no custom CSS unless necessary
- **Error handling**: Display user-friendly messages, avoid exposing technical details

### Database
- **UUID primary keys**: All tables use UUID strings, not integers
- **Timestamps**: All tables have `created_at` and `updated_at`
- **Indexes**: Add indexes for foreign keys and frequently queried fields
- **Migrations**: Never edit applied migrations, always create new ones
- **Testing**: Use in-memory SQLite for tests (configured in pytest)

## Developer Workflow Preferences

### Running Development Servers

**IMPORTANT**: Always run backend and frontend servers in **separate PowerShell terminals**, NOT in background processes within Claude Code.

**Terminal 1 - Backend**:
```powershell
cd C:\proyectos\devspell\backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```powershell
cd C:\proyectos\devspell\frontend
npm run dev
```

### Python Environment Management

**CRITICAL**: This project uses `uv` for all Python operations:
- **NEVER use `pip`** - always use `uv` commands
- **Virtual environment**: `uv` manages it automatically, but ensure it's activated for manual operations
- **Install dependencies**: `uv sync` (NOT `pip install`)
- **Run commands**: `uv run <command>` (automatically uses the venv)
- **Add packages**: `uv add <package>` (NOT `pip install <package>`)

**Before any Python installation or command**:
1. Verify you're in `backend/` directory
2. Use `uv run` prefix for all Python commands
3. Let `uv` handle the virtual environment automatically

### Workflow Best Practices

1. **Starting a development session**:
   - Terminal 1: Start PostgreSQL with `docker-compose up -d` in `backend/`
   - Terminal 2: Start backend API with `uv run uvicorn...`
   - Terminal 3: Start frontend with `npm run dev`
   - Keep all three terminals visible for monitoring logs

2. **Before making changes**:
   - Verify all services are running (green output in terminals)
   - Run `uv run pytest` to ensure current state is working

3. **After making changes**:
   - Check backend terminal for hot-reload confirmation
   - Check frontend terminal for compilation success
   - Test in browser before committing

## Current State (feature/frontend-auth branch)

**Completed**:
- JWT authentication (register, login, /me endpoint)
- Projects CRUD with ownership validation
- Code analysis engine (AST-based, cyclomatic complexity)
- Frontend auth flow (login/register/dashboard)
- PostgreSQL with 5 migrations applied
- Docker Compose environment

**In Progress/Next**:
- Connect dashboard to real projects data
- Analysis history per project
- Claude API integration for AI suggestions
- Advanced metrics and reporting

## Troubleshooting

**"Database connection refused"**: Ensure PostgreSQL is running (`docker-compose up -d`) and check port 5433

**"uv: command not found"**: Install uv with `pip install uv` or follow https://github.com/astral-sh/uv

**"Secret key not set"**: Generate with `uv run python -c "import secrets; print(secrets.token_urlsafe(32))"` and add to `.env`

**"Alembic can't find models"**: Models must be imported in `alembic/env.py` - check `target_metadata` assignment

**Frontend can't reach API**: Verify CORS_ORIGINS in backend `.env` includes frontend URL

**401 Unauthorized on protected endpoints**: Token may be expired (30min default) - re-login to get new token
