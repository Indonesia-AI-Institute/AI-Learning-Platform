# AI Learning Platform

A full-stack AI-powered learning platform that enables teachers to manage courses, classes, and tasks, while students can interact with AI through session-based chat tied to specific tasks. The platform includes a prompt analytics system that helps teachers understand how students engage with AI.

---

## Table of Contents

- [AI Learning Platform](#ai-learning-platform)
  - [Table of Contents](#table-of-contents)
  - [Tech Stack](#tech-stack)
  - [Architecture](#architecture)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [Docker: With the Repository](#docker-with-the-repository)
    - [Docker: Without Cloning the Repository](#docker-without-cloning-the-repository)
    - [Running Locally without Docker](#running-locally-without-docker)
  - [Environment Variables](#environment-variables)
  - [LLM Provider Configuration](#llm-provider-configuration)
  - [Database Migrations](#database-migrations)
  - [API Overview](#api-overview)
  - [Troubleshooting](#troubleshooting)
  - [License](#license)

---

## Tech Stack

**Backend**

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 15 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT via HttpOnly Cookie |
| Python | 3.11+ |

**Frontend**

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| State | TanStack Query |
| Package Manager | pnpm |

**Infrastructure**

| Component | Technology |
|-----------|-----------|
| Containerization | Docker + Docker Compose |
| Image Registry | GitHub Container Registry (GHCR) |

**Published images**

```
ghcr.io/indonesia-ai-institute/ai-learning-platform-api:latest
ghcr.io/indonesia-ai-institute/ai-learning-platform-frontend:latest
```

---

## Architecture

```
HTTP Request
    |
FastAPI Router  -->  RoleGuard (JWT + role validation)
    |
Service Layer   -->  Business logic
    |
    |-->  Repository  -->  SQLAlchemy  -->  PostgreSQL
    |
    |-->  LLM Layer   -->  Provider (OpenAI / OpenRouter / Gemini / Anthropic / Custom)
                           |
                           |--> SSE stream tokens to client
                           |
                           `--> Background: PromptClassifierAgent --> prompt_classifications table
```

When a student sends a message, two things happen in parallel: the LLM streams a response back to the client via SSE, and a background task classifies the prompt into 9 boolean categories and saves the result. This classification adds zero latency to the student experience.

## Prerequisites

- Docker 24+ and Docker Compose v2

For local development without Docker:
- Python 3.11
- Node.js 20+ and pnpm
- PostgreSQL 15

---

## Getting Started

### Docker: With the Repository

Use this approach if you want the full codebase, the ability to inspect the source, or to build images locally.

**1. Clone the repository**

```bash
git clone https://github.com/Indonesia-AI-Institute/AI-Learning-Platform.git
cd AI-Learning-Platform
```

**2. Configure environment**

```bash
cp .env.example .env
```

Fill in the required values in `.env`. See the [Environment Variables](#environment-variables) section for the full reference.

**3. Pull images from GHCR and start**

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

**4. Verify**

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs api --tail=30
```

**Building images locally (optional)**

If you have made changes to the source code and want to build images locally without pushing to the registry:

```bash
# Build all services
docker compose build

# Or build a specific service
docker compose build api
docker compose build frontend
```

To run with locally built images instead of the registry images:

```bash
docker compose up -d
```

`docker-compose.yml` uses the `build:` context, so `up` will use the locally built images. `docker-compose.prod.yml` uses only the registry images.

---

### Docker: Without Cloning the Repository

Use this approach if you want to run the platform directly from the published images without cloning the repository.

**1. Create a project folder**

```bash
mkdir ai-learning-platform && cd ai-learning-platform
```

**2. Create the environment file**

Create a file named `.env` in the folder and fill in the required values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ai_learning

# Must use "db" as host when running inside Docker
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@db:5432/ai_learning

SECRET_KEY=your_random_secret_key_minimum_32_characters
ACCESS_TOKEN_EXPIRE_MINUTES=60

DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_API_KEY=sk-or-xxxx

# URL accessible from the browser
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**3. Create a docker network**
```bash
docker network create ai-learning-net
```

**4. Run image**

Run image postgresql
```bash
docker run -d `
  --name db `
  --network ai-learning-net `
  --restart unless-stopped `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=your_password `
  -e POSTGRES_DB=ai_learning `
  -v pgdata:/var/lib/postgresql/data `
  -p 5432:5432 `
  postgres:15-alpine
```
Run image backend API

```bash
docker run -d `
  --name ailearning-api `
  --network ai-learning-net `
  --restart unless-stopped `
  --env-file .env `
  -p 8000:8000 `
  ghcr.io/indonesia-ai-institute/ai-learning-platform-api:latest
```
Run database migration

```bash
docker exec ailearning-api alembic upgrade head
```
Run image frontend

```bash
docker run -d `
  --name ailearning-frontend `
  --network ai-learning-net `
  --restart unless-stopped `
  -p 3000:3000 `
  ghcr.io/indonesia-ai-institute/ai-learning-platform-frontend:latest
```

**5. Verify**
The API will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

---



### Running Locally without Docker

**Backend**

```bash
# UV (Recommended)

uv venv --python 3.11
.venv/Scripts/Activate

# Windows

python -m venv .venv
.venv\Scripts\activate

# Mac / Linux

python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to use localhost, not "db"

# Run database migrations (PostgreSQL must be running)
alembic upgrade head

# Start the backend
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**

```bash
cd src/frontend
pnpm install
pnpm dev
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.

| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_USER` | Yes | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `POSTGRES_DB` | Yes | PostgreSQL database name |
| `DATABASE_URL` | Yes | Full async DB URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | Yes | JWT signing key, minimum 32 characters |
| `DEFAULT_LLM_PROVIDER` | Yes | `openai`, `openrouter`, `gemini`, `anthropic`, or `custom` |
| `DEFAULT_LLM_MODEL` | Yes | Model identifier for the selected provider |
| `NEXT_PUBLIC_API_URL` | Yes | API base URL accessible from the browser |

When running with Docker, `DATABASE_URL` must use `db` as the host (the Docker service name), not `localhost`.

---

## LLM Provider Configuration

Set `DEFAULT_LLM_PROVIDER` to one of the options below and fill in the corresponding variables.

**OpenRouter** (recommended for development — free models available)

```env
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_API_KEY=sk-or-xxxx
OPENROUTER_PROVIDER_ORDER=DeepInfra,SiliconFlow
OPENROUTER_ALLOW_FALLBACKS=true
```

**OpenAI**

```env
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-xxxx
```

**Google Gemini**

```env
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.0-flash
GEMINI_API_KEY=xxxx
```

**Anthropic**

```env
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_LLM_MODEL=claude-haiku-4-5
ANTHROPIC_API_KEY=sk-ant-xxxx
```

**Custom / Ollama (self-hosted)**

```env
DEFAULT_LLM_PROVIDER=custom
DEFAULT_LLM_MODEL=llama3.2
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1
CUSTOM_LLM_API_KEY=ollama
```

---

## Database Migrations

Migrations run automatically when the API container starts. For manual control:

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after changing a model
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1
```

When using Docker:

```bash
docker compose exec api alembic revision --autogenerate -m "describe your change"
docker compose exec api alembic upgrade head
```

---

## API Overview

All endpoints are prefixed with `/api/v1`.

| Group | Endpoints |
|-------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| Courses | `GET /courses`, `POST /courses`, `GET /courses/{id}`, `PUT /courses/{id}`, `DELETE /courses/{id}` |
| Classes | `GET /classes/my`, `POST /classes`, `POST /classes/{id}/enroll` |
| Tasks | `GET /tasks/class/{class_id}`, `POST /tasks/course/{course_id}`, `GET /tasks/{id}`, `PUT /tasks/{id}` |
| Chat (Student) | `POST /chat/sessions/task/{task_id}`, `GET /chat/sessions/{id}`, `POST /chat/sessions/{id}/stream`, `POST /chat/sessions/{id}/resume`, `DELETE /chat/sessions/{id}` |
| Chat (Teacher) | `GET /chat/teacher/student/{student_id}/sessions`, `GET /chat/teacher/sessions/{id}/history` |
| Analytics | `GET /analytics/me/classifications`, `GET /analytics/class/{id}/classifications`, `GET /analytics/task/{id}/classifications` |

Full interactive documentation is available at `http://localhost:8000/docs` when the server is running.

**Chat streaming**

The primary chat endpoint streams tokens via Server-Sent Events (SSE):

```
POST /api/v1/chat/sessions/{session_id}/stream
Content-Type: application/json
Cookie: access_token=<jwt>

{
  "messages": [{ "role": "user", "content": "Explain neural networks" }]
}
```

Response format:

```
data: Neural
data:  networks
data:  are...
data: [DONE]
```

---

## Troubleshooting

**API container exits immediately**

Check the logs:

```bash
docker compose logs api
```

The most common cause is an incorrect `DATABASE_URL`. When running inside Docker, the host must be `db`, not `localhost`.

**Migrations fail on startup**

If you see `alembic: command not found`, the image may not have been rebuilt after a `requirements.txt` change. Run:

```bash
docker compose build api && docker compose up -d api
```

**Frontend cannot reach the API**

`NEXT_PUBLIC_API_URL` is baked into the Next.js build at build time. Changing it in `.env` alone is not enough — you must rebuild the frontend image:

```bash
docker compose build frontend && docker compose up -d frontend
```

For local development, the value should be `http://localhost:8000/api/v1`.

**GHCR authentication error when pulling**

If you see a `403` or `unauthorized` error when running `docker compose pull`, the package may be private. Log in first:

```bash
echo YOUR_GITHUB_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Make sure the PAT has the `read:packages` scope.

---

## License

Internal Use — AI Learning Platform
