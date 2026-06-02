# Nexus — AI-Powered Workspace Platform

> Manage projects, tasks, and teams — supercharged with AI. Built for modern SaaS companies.

Nexus is a production-grade, multi-tenant SaaS backend that combines project management, team collaboration, and AI assistance into a single powerful API. Think Jira + Notion + AI Assistant — one backend, built to scale.

---

## What Is Nexus?

Companies use Nexus to:

- **Manage projects and tasks** — create, assign, track, and prioritize work across teams
- **Collaborate with role-based access** — owners, admins, members, and viewers per organization
- **Generate tasks with AI** — describe a project, let AI break it into actionable tasks
- **Stay organized** — activity logs, status tracking, and smart summaries

Each company (tenant) gets fully isolated data — one platform, thousands of organizations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6 + Django REST Framework |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Background Jobs | Celery |
| Auth | JWT (SimpleJWT) |
| AI | Claude API (Anthropic) |
| Infrastructure | Docker + Docker Compose |
| Production Server | Gunicorn |

---

## API Endpoints

All endpoints are versioned under `/api/v1/`.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Create a new account |
| POST | `/api/v1/auth/login/` | Login and receive JWT tokens |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token |

### Coming Soon
- `/api/v1/organizations/` — create and manage organizations
- `/api/v1/projects/` — projects scoped per organization
- `/api/v1/tasks/` — tasks with status, priority, and assignment
- `/api/v1/ai/generate-tasks/` — AI-powered task generation
- `/api/v1/ai/summarize-project/` — AI project summaries

---

## Standard Response Format

Every endpoint returns a consistent envelope:

```json
{
  "success": true,
  "message": "Account created successfully",
  "data": { ... },
  "errors": null
}
```

---

## Getting Started

### Prerequisites
- Python 3.13
- Docker Desktop

### 1. Clone the repo
```bash
git clone <repo-url>
cd ai-saas-backend
```

### 2. Create `.env` file in the root
```env
SECRET_KEY=your-secret-key-here
POSTGRES_DB=saas_db
POSTGRES_USER=saas_user
POSTGRES_PASSWORD=saas_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 3. Start infrastructure
```bash
docker-compose up -d
```

### 4. Set up the Django app
```bash
cd services/core_api
py -3.13 -m venv venv
source venv/Scripts/activate      # Windows (Git Bash)
# or: venv\Scripts\activate       # Windows (PowerShell)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`

---

## Architecture

```
services/core_api/
├── config/          → Settings (base / dev / prod), URLs
├── common/          → BaseModel, standard response helpers
└── apps/
    ├── users/       → Custom User model, JWT auth
    ├── organizations/ → Organizations + Memberships + Roles
    ├── projects/    → (coming soon)
    ├── tasks/       → (coming soon)
    ├── subscriptions/ → (coming soon)
    └── ai_assistant/  → (coming soon)
```

Each app follows a strict layered pattern:

```
views.py       → HTTP only (no business logic)
serializers.py → Input validation + output shaping
services.py    → All business logic lives here
models.py      → Database schema
```

---

## License

Private — all rights reserved.
