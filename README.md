# FastAPI DDD Template

A modern FastAPI application template built with Domain-Driven Design (DDD) principles, featuring JWT authentication, PostgreSQL database, and Docker containerization.

## 🏗️ Architecture Overview

This application follows Domain-Driven Design (DDD) patterns and Clean Architecture principles to ensure maintainable, testable, and scalable code.

### Project Structure

```
teacher/
├── src/
│   ├── app/                    # Application Layer (HTTP handlers, schemas)
│   │   └── auth/              # Authentication endpoints
│   ├── domain/                # Domain Layer (business logic)
│   │   ├── user/             # User aggregate and business rules
│   ├── infra/                 # Infrastructure Layer (database, external services)
│   │   ├── migrations/       # Alembic database migrations
│   │   └── user/            # User repository implementation
│   ├── server.py             # FastAPI application setup
│   └── settings.py           # Application configuration
├── tests/                     # Test files
├── docker-compose.yml         # Docker services configuration
├── Dockerfile                 # Container definition
├── Makefile                   # Development commands
└── pyproject.toml            # Project dependencies and configuration
```

## 🎯 Domain-Driven Design Implementation

### 1. Domain Layer (`src/domain/`)

The core business logic layer containing:

- **Aggregates**: Business entities that encapsulate domain logic
  - `User`: Handles user creation, authentication, and authorization
- **DTOs (Data Transfer Objects)**: Simple data containers for transferring data between layers
- **Repository Interfaces**: Abstract contracts for data access
- **Domain Errors**: Business-specific exceptions

**Example - User Aggregate:**
```python
class User:
    def __init__(self, repo: IUserRepo):
        self._repo = repo
    
    async def create(self, create_data: CreateUserDTO) -> UserDTO:
        # Business logic for user creation
        existed_user = await self.find_by_username(create_data.username)
        if existed_user:
            raise UserAlreadyExistsError("User with this username already exists.")
        # ... password hashing and creation logic
```

### 2. Application Layer (`src/app/`)

HTTP request/response handling and orchestration:

- **Handlers**: FastAPI route handlers that coordinate domain operations
- **Schemas**: Pydantic models for request/response validation
- **Dependencies**: FastAPI dependency injection for aggregates and repositories

### 3. Infrastructure Layer (`src/infra/`)

External concerns and implementations:

- **Database Models**: SQLAlchemy models for data persistence
- **Repository Implementations**: Concrete implementations of domain repository interfaces
- **Base Repository**: Generic repository pattern with common CRUD operations
- **Migrations**: Alembic database schema management

## 🔧 Key Features

### Authentication & Authorization
- JWT token-based authentication
- Password hashing with salt
- OAuth2 password flow
- Protected endpoints with dependency injection

### Database Management
- PostgreSQL with async SQLAlchemy
- Alembic migrations for schema management
- Repository pattern for data access abstraction
- Generic base repository with common operations

### Development Tools
- Docker & Docker Compose for containerization
- UV for fast Python package management
- Comprehensive linting (Ruff, Flake8, MyPy)
- Structured logging
- CORS middleware for API access

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.13+ (for local development)
- UV package manager

### Environment Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd teacher
```

2. **Create environment file:**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=teacher

# Authentication
AUTH_SECRET_KEY=your-super-secret-jwt-key-here
AUTH_PASSWORD_SALT=your-password-salt-here
```

### Running with Docker (Recommended)

```bash
# Start all services
make up

# Or manually:
docker compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI application on port 8088

### Local Development Setup

```bash
# Install dependencies
uv sync

# Start database only
docker compose up -d db

# Run migrations
make migrate

# Start the application
uv run uvicorn src.server:app --reload --host 0.0.0.0 --port 8088
```

## 📊 Database Migrations

The application uses Alembic for database schema management:

```bash
# Create new migration
make make_migrations

# Apply migrations
make migrate

# Rollback migration
make migrate_down
```

## 🧪 API Endpoints

### Authentication

**Register User:**
```http
POST /auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "password": "secure_password"
}
```

**Login:**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=secure_password
```

**Get Current User:**
```http
GET /auth/me
Authorization: Bearer <jwt_token>
```

## 🛠️ Development Commands

The `Makefile` provides convenient development commands:

```bash
# Docker operations
make up          # Start all services
make down        # Stop all services  
make restart     # Restart all services
make rebuild     # Rebuild and restart services

# Code quality
make lint        # Run all linters (ruff, flake8, mypy)
make lint_fix    # Auto-fix linting issues

# Database operations
make make_migrations  # Create new migration
make migrate         # Apply migrations
make migrate_down    # Rollback migration
```

## 📝 Code Quality

The project enforces high code quality standards:

- **Ruff**: Fast Python linter and formatter
- **Flake8**: Additional linting rules
- **MyPy**: Static type checking with strict mode
- **Comprehensive linting rules**: Import sorting, code complexity, security checks

### Linting Configuration

```bash
# Check code quality
make lint

# Auto-fix issues
make lint_fix
```

## 🏛️ Architecture Patterns

### Repository Pattern
Abstract data access through interfaces:
```python
class IUserRepo(Protocol):
    async def create(self, user: UserDTO) -> UserDTO: ...
    async def find_by_username(self, username: str) -> UserDTO | None: ...
```

### Dependency Injection
Clean separation of concerns using FastAPI's DI:
```python
async def user_aggregate_di(repo: IUserRepo = Depends(user_repo_di)) -> User:
    return User(repo=repo)
```

### Generic Base Repository
Reusable CRUD operations:
```python
class BaseRepository(Generic[DBModel, DTO, IDType], ABC):
    async def get_by_id(self, entity_id: IDType) -> DTO | None: ...
    async def create(self, dto: DTO) -> DTO: ...
    async def update(self, dto: DTO) -> DTO: ...
    async def delete(self, entity_id: IDType) -> None: ...
```

## 🔒 Security Features

- JWT tokens with configurable expiration
- Password hashing with salt
- CORS middleware configuration
- Input validation with Pydantic
- SQL injection prevention through SQLAlchemy ORM

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework with automatic API documentation
- **SQLAlchemy**: Async ORM for database operations
- **Alembic**: Database migration management
- **AsyncPG**: High-performance PostgreSQL adapter
- **PyJWT**: JSON Web Token implementation
- **Pydantic**: Data validation and settings management

### Development Dependencies
- **Ruff**: Fast linter and formatter
- **MyPy**: Static type checker
- **Pytest**: Testing framework
- **Flake8**: Additional linting rules

## 🚦 Health Checks

The application includes health checks for:
- Database connectivity
- Application status

Access at: `http://localhost:8088/`

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8088/docs
- **ReDoc**: http://localhost:8088/redoc
- **OpenAPI Schema**: http://localhost:8088/openapi.json

## 🤝 Contributing

1. Follow the established DDD patterns
2. Maintain high test coverage
3. Run linting before committing: `make lint`
4. Use conventional commit messages
5. Update documentation for new features
