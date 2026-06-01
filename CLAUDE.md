# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `services/core_api/`:

```bash
# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Run development server
python manage.py runserver

# Django shell
python manage.py shell
```

Django settings module: `config.settings.dev` (development) or `config.settings.prod` (production). The `DJANGO_SETTINGS_MODULE` env var controls which is loaded.

## Architecture

Single Django service (`services/core_api/`) structured as layered apps.

**Per-app layers:**
- `models.py` — database schema, all inherit from `common.models.BaseModel` (UUID PK, `created_at`, `updated_at`)
- `serializers.py` — DRF serializers for request validation and response shaping
- `services.py` — business logic; service classes use Pydantic `BaseModel` inputs for type safety
- `views.py` — thin HTTP handlers that call services and return standardized responses
- `urls.py` — URL routing, registered under `/api/v1/`

**Apps:**
- `apps/users` — custom `User` model (UUID PK, email as username), JWT auth (register/login/logout via token blacklisting)
- `apps/organizations` — `Organization` + `Membership` models; roles are `owner/admin/member/viewer`; planned `OrganizationScopedMixin` for multi-tenant query scoping
- Future apps per `PROJECT.md`: `projects`, `tasks`, `subscriptions`, `activity`, `ai_assistant`

**Shared utilities (`common/`):**
- `common.models.BaseModel` — base for all models
- `common.response` — `success_response()`, `error_response()`, `format_errors()`; every view must use these, never return raw `Response({...})` directly

**Standard response envelope:**
```json
{ "success": bool, "message": str, "data": any, "errors": list | null }
```
`format_errors(serializer.errors)` converts DRF error dicts into `[{field, message, code}]` lists for the `errors` field.

## Key conventions

- Business logic lives in `services.py`, not views. Views call services and return responses.
- Service method inputs are typed with Pydantic `BaseModel` (see `AuthService` in `apps/users/services.py`).
- All URLs are versioned under `/api/v1/`.
- Settings are split: `config/settings/base.py` (shared), `dev.py` (PostgreSQL on localhost), `prod.py` (security headers).
- Docker Compose provides PostgreSQL 16 on port 5432 and Redis 7 on port 6379; connection details come from `.env`.
