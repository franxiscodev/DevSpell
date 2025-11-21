# DevSpell 🔮

> Static code analyzer for Python with AI-powered suggestions using Ollama + DeepSeek-Coder

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/franxiscodev/DevSpell/releases/tag/v0.2.0)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

DevSpell is a modern, production-grade code analysis platform that helps developers improve their Python code quality through static analysis and AI-powered suggestions. Built as an educational project to master full-stack development with Claude Code.

## ✨ Features

### Code Analysis
- 📊 **Static Analysis**: AST-based code parsing with cyclomatic complexity calculation
- 🔍 **Detailed Metrics**: Lines of code, number of functions, imports, and more
- 📝 **Function Analysis**: Per-function complexity, parameters, and documentation
- 📈 **Analysis History**: Save and track analysis results over time
- 🔢 **Line Numbers**: Code editor with synchronized line numbering for easy error location

### AI-Powered Suggestions
- 🤖 **Local AI**: 100% free Ollama integration with DeepSeek-Coder 1.3b model
- 💡 **Smart Suggestions**: 2-4 concrete, actionable improvements per analysis
- 🌐 **Bilingual**: Suggestions in Spanish with technical terms in English
- 🔒 **Privacy-First**: All AI processing happens locally, data never leaves your system
- ⚡ **Fast & Lightweight**: Model is only 800MB with 2-4GB RAM usage

### Project Management
- 👤 **User Authentication**: Secure JWT-based authentication with Argon2 password hashing
- 📂 **Projects CRUD**: Create, update, delete, and organize analysis projects
- 🔐 **Ownership**: Projects are user-specific with proper authorization
- 📊 **Dashboard**: Centralized view of all projects and recent analyses

### Developer Experience
- 🎨 **Modern UI**: Built with Next.js 16, TypeScript, and TailwindCSS
- 🚀 **Fast API**: FastAPI backend with async/await throughout
- 🐳 **Docker Ready**: Complete Docker Compose setup for easy deployment
- 📝 **Type Safety**: Full TypeScript frontend with Pydantic backend schemas
- 🔄 **Hot Reload**: Development servers with instant feedback

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+ (modern type hints with `|` syntax)
- **Database**: PostgreSQL 16 (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT with Argon2 password hashing
- **Package Manager**: uv (fast, modern alternative to pip)
- **AI**: Ollama + DeepSeek-Coder 1.3b (local, free)

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: TailwindCSS 3
- **State**: React hooks + localStorage
- **API Client**: Custom TypeScript client with automatic auth injection

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL 16-alpine
- **AI Runtime**: Ollama (Docker)
- **Reverse Proxy**: Ready for Nginx/Traefik

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with npm
- **Docker** and **Docker Compose**
- **Git** (with `gh` CLI recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/franxiscodev/DevSpell.git
cd DevSpell
```

2. **Backend setup**
```bash
cd backend

# Copy environment file and configure
cp .env.example .env
# Edit .env: Set POSTGRES_PASSWORD and SECRET_KEY
# Generate SECRET_KEY: uv run python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start services (PostgreSQL + Ollama)
docker-compose up -d

# Install Python dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Download AI model (~800MB, one-time)
docker exec -it devspell-ollama ollama pull deepseek-coder:1.3b

# Start backend server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

4. **Access the application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### First Use

1. Navigate to http://localhost:3000
2. Click "Register" and create an account
3. Login with your credentials
4. Create a new project
5. Paste Python code and click "Analizar Código"
6. View metrics and click "Obtener sugerencias" for AI insights

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete project documentation for Claude Code
- **[Setup Guide](backend/DOCKER_SETUP.md)** - Detailed Docker and environment setup
- **[Future Sprints](temp/SPRINT_FUTURO_AI_SUGGESTIONS.md)** - Planned features and enhancements

## 🛠️ Development

### Running Tests
```bash
cd backend
uv run pytest                    # Run all tests
uv run pytest -v -s              # Verbose with print output
uv run pytest tests/test_analyzer.py  # Specific test file
```

### Database Migrations
```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Code Quality
```bash
# Backend linting
cd backend
uv run ruff check .              # Check
uv run ruff check --fix .        # Auto-fix

# Frontend linting
cd frontend
npm run lint
```

## 🐳 Docker Deployment

### Production Build
```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables
See `.env.example` files for required configuration:
- `backend/.env.example` - Backend configuration
- `frontend/.env.local.example` - Frontend configuration (optional)

## 📊 Project Structure

```
DevSpell/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/routes/     # REST endpoints
│   │   ├── auth/           # Authentication & authorization
│   │   ├── projects/       # Projects CRUD
│   │   ├── analysis/       # Analysis history
│   │   ├── services/       # Business logic
│   │   │   └── ai/        # AI providers (Ollama)
│   │   ├── core/          # Config, database, logging
│   │   └── models/        # Pydantic schemas
│   ├── tests/             # Pytest tests
│   ├── alembic/           # Database migrations
│   └── docker-compose.yml # Services: PostgreSQL + Ollama
│
├── frontend/              # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   │   ├── ai/          # AI suggestions panel
│   │   ├── analyzer/    # Code editor, results
│   │   └── auth/        # Login, register forms
│   ├── lib/api/         # API client
│   └── types/           # TypeScript types
│
├── docs/                # Sprint documentation
├── temp/                # Temporary files, screenshots, plans
├── CLAUDE.md           # Project guide for Claude Code
└── README.md           # This file
```

## 🎯 Roadmap

### v0.3.0 (Next Release)
- [ ] Save AI suggestions with analysis in database
- [ ] Display saved suggestions in analysis detail page
- [ ] Export analysis results (PDF, Markdown)
- [ ] Analysis comparison tool

### v0.4.0
- [ ] Security analysis (detect SQL injection, XSS, etc.)
- [ ] Performance bottleneck detection
- [ ] Code refactoring suggestions with automatic application
- [ ] Team collaboration features

### v1.0.0
- [ ] Multi-language support (JavaScript, TypeScript, Go)
- [ ] Cloud provider integration (Gemini, Claude)
- [ ] CI/CD integration (GitHub Actions, GitLab CI)
- [ ] Custom rule engine

## 🤝 Contributing

This is an educational project, but contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with guidance from **Claude Code** by Anthropic
- Powered by **Ollama** and **DeepSeek-Coder** for local AI
- Inspired by tools like **SonarQube**, **PyLint**, and **Ruff**
- UI/UX inspired by modern developer tools

## 📧 Contact

**Francisco** - [@franxiscodev](https://github.com/franxiscodev)

Project Link: [https://github.com/franxiscodev/DevSpell](https://github.com/franxiscodev/DevSpell)

---

<p align="center">
Made with ❤️ and Claude Code
</p>
