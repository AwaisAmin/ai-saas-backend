# AI Task & Workspace Platform — Enterprise SaaS Backend

> **Jira + Notion + Slack + AI Assistant** — ek hi backend mein
>
> Yeh document is poore project ka "brain" hai. Naya session start ho ya purana — yahan se context milta hai.

---

## Vision

Ek production-grade, multi-tenant SaaS backend banana jo:
- Multiple companies (tenants) ko isolate rakhe
- Teams ko projects & tasks manage karne de
- AI assistant se tasks generate kare, summaries de
- Millions of users tak scale kare
- Real companies ki tarah likha gaya ho (clean, layered, tested)

---

## Tech Stack

| Layer | Technology | Kyun? |
|---|---|---|
| Language | Python 3.12 | Industry standard for backend + AI |
| Framework | Django + DRF | Battle-tested, batteries included |
| Database | PostgreSQL | Production-grade relational DB |
| Cache | Redis | Fast in-memory cache + Celery broker |
| Background Jobs | Celery | Async tasks (emails, AI calls, reports) |
| Auth | JWT (SimpleJWT) | Stateless, scalable auth |
| AI | Claude API (Anthropic) | Task generation, summaries |
| Containerization | Docker + Docker Compose | Consistent environments |
| Server | Gunicorn + Nginx | Production WSGI serving |
| API Docs | drf-spectacular (OpenAPI) | Self-documenting APIs |

---

## Current Status

```
[DONE]
✅ Django project initialized (core_api service)
✅ Users app created
✅ Docker setup (basic)
✅ Virtual environment + dependencies (celery, gunicorn, psycopg2)

[IN PROGRESS]
🔄 Custom User model (email-based login)
🔄 PostgreSQL connection

[TODO — Phases below]
```

---

## Project Architecture

```
ai-saas-backend/
├── services/
│   └── core_api/               ← Main Django service
│       ├── config/             ← Settings, URLs, WSGI/ASGI
│       ├── apps/
│       │   ├── users/          ← Custom User model, auth
│       │   ├── organizations/  ← Tenants, memberships
│       │   ├── projects/       ← Projects per org
│       │   ├── tasks/          ← Tasks, assignments
│       │   ├── subscriptions/  ← Plans, billing
│       │   ├── activity/       ← Audit logs
│       │   └── ai_assistant/   ← AI features
│       ├── common/             ← Shared: base models, permissions, utils
│       └── manage.py
├── docker-compose.yml
├── .env
└── PROJECT.md                  ← (this file)
```

### Layered Architecture (Har App Mein)
```
views.py       → Request/Response only (HTTP layer)
serializers.py → Validation + Data shape
services.py    → Business logic (ye sabse important file hai)
models.py      → Database schema + basic queries
admin.py       → Django admin config
```

> **Rule:** Views ko business logic nahi pata honi chahiye. Services mein sab kuch hota hai.

---

## Data Models (Final Schema)

### 1. User
```
id          UUID (PK)
email       unique, indexed
password    hashed
first_name
last_name
is_active   bool
is_verified bool (email verify)
created_at
updated_at
```

### 2. Organization (Tenant)
```
id          UUID (PK)
name
slug        unique (url-friendly)
logo_url
plan        (free/pro/enterprise)
is_active   bool
created_at
```

### 3. Membership (User ↔ Organization)
```
id          UUID (PK)
user        FK → User
org         FK → Organization
role        (owner/admin/member/viewer)
joined_at
is_active   bool
```
> One user can be in multiple orgs. One org has many users.

### 4. Project
```
id          UUID (PK)
org         FK → Organization  ← tenant isolation
name
description
status      (active/archived)
owner       FK → User
created_at
updated_at
```

### 5. Task
```
id          UUID (PK)
project     FK → Project
title
description
status      (todo/in_progress/in_review/done)
priority    (low/medium/high/critical)
assignee    FK → User (nullable)
due_date    date (nullable)
ai_generated bool
created_by  FK → User
created_at
updated_at
```

### 6. Subscription
```
id                   UUID (PK)
org                  OneToOne → Organization
plan                 (free/pro/enterprise)
status               (active/cancelled/past_due)
current_period_start date
current_period_end   date
stripe_customer_id   string
stripe_sub_id        string
```

### 7. ActivityLog
```
id          UUID (PK)
org         FK → Organization
user        FK → User (nullable)
action      (task_created / member_invited / etc.)
entity_type (task / project / membership)
entity_id   UUID
metadata    JSONB
created_at
```
> Har important action log hota hai. Audit trail ke liye.

---

## Multi-Tenant Design

```
Request → Auth → Extract User → Extract User's Org → Filter all queries by org
```

- Koi bhi query bina `org` filter ke nahi chalegi
- `common/mixins.py` mein `OrganizationScopedMixin` banega
- `get_queryset()` hamesha `org=self.request.org` use karega

---

## API Design

### Versioning
```
/api/v1/auth/
/api/v1/users/
/api/v1/organizations/
/api/v1/projects/
/api/v1/tasks/
/api/v1/subscriptions/
/api/v1/ai/
```

### Auth Flow
```
POST /api/v1/auth/register/       → Account banao
POST /api/v1/auth/login/          → JWT tokens lo (access + refresh)
POST /api/v1/auth/token/refresh/  → Access token refresh karo
POST /api/v1/auth/logout/         → Refresh token blacklist karo
```

### Standard Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Task created successfully",
  "errors": null
}
```

---

## Development Phases (Step-by-Step Roadmap)

### PHASE 1 — Foundation (Current)
**Goal:** Project chalaye, database connect ho, user register/login kare

- [ ] Custom User model (email as username)
- [ ] PostgreSQL connect karo (SQLite hata do)
- [ ] Settings split karo (base / dev / prod)
- [ ] JWT auth (register, login, logout, refresh)
- [ ] Email verification (Celery task)
- [ ] `.env` properly use karna
- [ ] Custom response format

**Seekhoge:** Django custom auth, env management, JWT

---

### PHASE 2 — Multi-Tenancy
**Goal:** Organizations banao, users join karen, roles set karen

- [ ] Organization model + CRUD
- [ ] Membership model (invite system)
- [ ] Role-based permissions (owner/admin/member/viewer)
- [ ] Organization middleware (request mein org inject karo)
- [ ] `OrganizationScopedMixin` — har view mein tenant isolation

**Seekhoge:** Multi-tenancy patterns, custom permissions, middleware

---

### PHASE 3 — Core Business Logic
**Goal:** Projects aur Tasks fully working

- [ ] Projects CRUD (org-scoped)
- [ ] Tasks CRUD with status/priority
- [ ] Task assignment (member ko)
- [ ] Filtering, searching, pagination (DRF filters)
- [ ] `services.py` layer — business logic views se alag
- [ ] ActivityLog — har action record karo

**Seekhoge:** Service layer pattern, DRF filters, audit logging

---

### PHASE 4 — Performance & Caching
**Goal:** APIs fast rakho, DB pe load kam karo

- [ ] Redis setup
- [ ] `django-redis` cache backend
- [ ] Cache frequently read data (org details, user profile)
- [ ] `select_related` / `prefetch_related` — N+1 queries khatam
- [ ] Database indexes — consciously add karo
- [ ] Django Debug Toolbar (dev mein queries dekho)

**Seekhoge:** Query optimization, Redis caching, DB indexing

---

### PHASE 5 — Background Jobs
**Goal:** Heavy/async kaam Celery se karo

- [ ] Celery + Redis broker setup
- [ ] Email sending (async)
- [ ] Activity log writing (async)
- [ ] Celery Beat — scheduled tasks (subscription reminders, reports)
- [ ] Task monitoring (Flower)

**Seekhoge:** Distributed task queues, async patterns

---

### PHASE 6 — Subscriptions & Billing
**Goal:** Plans manage karo, free limits enforce karo

- [ ] Subscription model
- [ ] Plan limits (free: 3 projects, 5 members max)
- [ ] `can_create_project()` type permission checks
- [ ] Stripe webhook handling (optional/advanced)

**Seekhoge:** Business rules, feature gating, webhooks

---

### PHASE 7 — AI Assistant
**Goal:** Claude API se AI features add karo

- [ ] `ai_assistant` app
- [ ] `POST /api/v1/ai/generate-tasks/` — project description se tasks banao
- [ ] `POST /api/v1/ai/summarize-project/` — project summary
- [ ] Rate limiting per org (free: 10 AI calls/day)
- [ ] AI results ActivityLog mein record karo
- [ ] Celery se async AI calls

**Seekhoge:** AI API integration, rate limiting, context building

---

### PHASE 8 — Production Hardening
**Goal:** Real server pe deploy karo, production-safe banao

- [ ] Settings: base / dev / prod properly split
- [ ] Gunicorn config (workers, timeout)
- [ ] Nginx config
- [ ] Structured logging (JSON logs, log levels)
- [ ] Rate limiting (DRF throttling)
- [ ] Security headers (CORS, HTTPS, etc.)
- [ ] Health check endpoints
- [ ] Docker Compose production config
- [ ] `.env` secrets management

**Seekhoge:** Production deployment, security, observability

---

### PHASE 9 — Testing
**Goal:** Code confident karo — bugs se bachao

- [ ] Unit tests — models, services
- [ ] Integration tests — API endpoints
- [ ] Factory Boy — test data banana
- [ ] pytest-django setup
- [ ] Coverage report

**Seekhoge:** TDD mindset, test patterns

---

## SOLID Principles — Iss Project Mein Kaise Apply Honge

| Principle | Matlab | Example in This Project |
|---|---|---|
| **S** — Single Responsibility | Har class/function ek kaam kare | `TaskService` sirf task logic, `EmailService` sirf emails |
| **O** — Open/Closed | Extend karo, modify mat karo | Base serializer extend karna |
| **L** — Liskov Substitution | Subclasses parent ki jagah kaam karen | Custom permission classes |
| **I** — Interface Segregation | Chote interfaces banao | `OrganizationScopedMixin` sirf wahi de jo chahiye |
| **D** — Dependency Inversion | High-level modules low-level pe depend na karen | Services ke andar managers use karo, direct queries nahi |

---

## Key Conventions (Hamesha Follow Karo)

1. **UUID primary keys** — integer IDs expose mat karo
2. **`created_at`, `updated_at`** — har model mein (auto)
3. **Soft delete** where needed — `is_active=False`, hard delete nahi
4. **Never put logic in views** — views sirf HTTP handle kare
5. **Services layer mandatory** — business logic sirf `services.py` mein
6. **All queries org-scoped** — multi-tenant security
7. **Env variables for secrets** — hardcode bilkul nahi
8. **Migrations always commit** — hamesha migrations commit karo
9. **API versioning from day 1** — `/api/v1/`
10. **Structured logging** — `logger.info()` with context, `print()` bilkul nahi

---

## Earnings Potential (After Completion)

Yeh project complete karne ke baad:
- **Freelancing:** Django + DRF + PostgreSQL + Redis + Celery + AI = $50-150/hr internationally
- **Job Market:** Backend Engineer role at product companies (Remote/Lahore)
- **Own Product:** Iss codebase ko actual SaaS mein convert kar sako
- **Portfolio:** Enterprise-grade project jo interviewers impress kare

---

## Session Shorthand (Naye Session Mein Quickly Context Dene Ke Liye)

Jab naya session shuru ho, bas itna bolo:
> "PROJECT.md padho, hum Phase X mein hain, [specific task] karna hai"

---

*Last Updated: 2026-03-05 | Current Phase: 1 — Foundation*
