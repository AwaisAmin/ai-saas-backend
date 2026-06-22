# NexTask

![CI](https://github.com/AwaisAmin/ai-saas-backend/actions/workflows/ci.yml/badge.svg)

Production-grade, multi-tenant SaaS backend for project management and AI-assisted task automation. Built with Django, Celery, and a provider-agnostic AI layer.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6 + Django REST Framework |
| Database | PostgreSQL 16 |
| Cache & Queue | Redis 7 + Celery |
| Auth | JWT (SimpleJWT) |
| AI | Claude / OpenAI / Gemini (provider-agnostic) |
| Infrastructure | Docker + Docker Compose |
| Server | Gunicorn |
| Monitoring | Sentry |

---

## Quick Start

**Prerequisites:** Python 3.13, Docker Desktop

```bash
# 1. Clone
git clone <repo-url>
cd ai-saas-backend

# 2. Create .env (see .env.example)
cp .env.example .env

# 3. Start PostgreSQL + Redis
docker-compose up -d

# 4. Install & migrate
cd services/core_api
pip install -r requirements.txt
python manage.py migrate

# 5. Run
python manage.py runserver
```

API docs available at `http://localhost:8000/api/docs/`

---

## Architecture

```
services/
├── core_api/          Django — auth, orgs, projects, tasks, billing
│   ├── apps/
│   │   ├── core/      users, organizations
│   │   ├── workspace/ projects, tasks, activity
│   │   ├── billing/   subscriptions, payments
│   │   └── intelligence/  AI views + rate limiting
│   └── common/        BaseModel, response helpers, mixins
│
└── ai_service/        FastAPI — stateless AI service
    └── providers/     Claude, OpenAI, Gemini
```

---

## Testing

```bash
cd services/core_api
pytest tests/ -v
```

62 tests · 80%+ coverage · CI runs on every push via GitHub Actions.

---

## License

Private — all rights reserved.
