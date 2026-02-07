# Production Readiness Roadmap (2 Weeks)

## Goal
Move the current FastAPI pet project closer to production standards without overengineering.

## Week 1 — Solid Foundation

### Day 1: Config and environment
- [x] Move all critical settings to typed config (`pydantic-settings`): DB URL, JWT secret, token TTL, app env.
- [ ] Add strict startup checks (fail fast if required secrets are missing).
- [x] Split configs for `dev` / `test` / `prod`.

### Day 2: Database and migrations
- [x] Prepare PostgreSQL runtime config (keep SQLite only for tests if needed).
- [x] Validate and clean Alembic flow (generate + apply migration in CI/local).
- [x] Add DB indexes for frequent queries (orders by customer, items by category, etc.).

### Day 3: API hardening
- [ ] Add global exception handlers with consistent error schema.
- [ ] Add request validation edge cases to tests (bad payloads, malformed auth headers).
- [ ] Normalize response models for all routers (avoid raw ORM responses).

### Day 4: Security basics
- [ ] Remove hardcoded secrets; use env-only.
- [ ] Add refresh token flow (access + refresh) and logout/revoke logic.
- [ ] Add simple role checks where sensitive endpoints exist.

### Day 5: Observability basics
- [ ] Structured logging (JSON) with request id/correlation id.
- [ ] Add `/health/live` and `/health/ready`.
- [ ] Add Sentry (or similar) for runtime error tracking.

### Day 6-7: CI quality gates
- [ ] Extend GitHub Actions: `pytest`, coverage threshold, `ruff`, optional `mypy`.
- [ ] Add security checks: `pip-audit` (and optionally `bandit`).
- [ ] Ensure branch protection requires green CI checks.

## Week 2 — Background jobs and deployment shape

### Day 8: Async tasks introduction (Celery)
- [ ] Add Redis + Celery worker in `docker-compose`.
- [ ] Move heavy/non-blocking operations (e.g., image processing) to Celery tasks.
- [ ] Add task status/result endpoint if needed.

### Day 9: Reliability for background jobs
- [ ] Configure retries, exponential backoff, and dead-letter strategy (basic).
- [ ] Add idempotency protection for repeated task triggers.
- [ ] Add integration tests for task-triggering API paths.

### Day 10: API performance and limits
- [ ] Add rate limiting for auth and mutation endpoints.
- [ ] Add pagination/filtering/sorting for list endpoints.
- [ ] Optimize obvious N+1 patterns and query plans.

### Day 11: Deployment baseline
- [ ] Finalize Docker images (multi-stage if needed).
- [ ] Add `gunicorn + uvicorn workers` settings for production run.
- [ ] Put reverse proxy in front (Nginx) with proper timeouts and static handling.

### Day 12: Data and backup readiness
- [ ] Define PostgreSQL backup strategy (daily dump + restore test).
- [ ] Add migration rollback checklist.
- [ ] Document maintenance commands.

### Day 13: Documentation for ops and onboarding
- [ ] Add `RUNBOOK.md`: startup, common failures, rollback steps.
- [ ] Add API auth flow docs (login/refresh/logout) with examples.
- [ ] Update README with architecture and CI badges.

### Day 14: Final production readiness check
- [ ] Run full CI + smoke tests in clean environment.
- [ ] Validate health endpoints, logs, and error alerts.
- [ ] Freeze release checklist for v1.

## What to postpone for now
- Kafka/event bus (introduce only when you have multiple services and real event streaming needs).
- Full microservices split.
- Advanced tracing stack if team/project size is still small.

## Minimal target after this roadmap
- Stable CI with quality gates.
- 90%+ business-logic test confidence retained.
- Secure auth baseline and predictable deploy/runtime behavior.
- Async workload handled via Celery + Redis.
