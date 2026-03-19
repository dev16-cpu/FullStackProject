# FullStack Deployment Guide

This workspace originally contained several standalone Flask exercises. It now includes one deployment target at the repository root:

- `wsgi.py` is the production entrypoint.
- `fullstack_app/` contains the deployable Flask application.
- The older exercise folders remain in place for reference.

## What is deployable now

The root app exposes these routes:

| Route | Description |
|-------|-------------|
| `/` | Home page for the workspace |
| `/health` | JSON health-check endpoint (`{"status":"ok"}`) |
| `/students` | Jinja list example |
| `/form-demo` | Validated form example (server-side) |
| `/auth/register` | SQLAlchemy-backed registration |
| `/auth/login` | SQLAlchemy-backed login |
| `/auth/logout` | POST — ends the current session |

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update values.
4. Start the app:

   ```bash
   python wsgi.py
   ```

## Running the tests

```bash
pytest
```

All tests live in the `tests/` directory. A fixture creates an in-memory SQLite database so no external services are needed.

## Production configuration

Set these environment variables in your hosting platform:

- `SECRET_KEY`: required, use a long random value
- `DATABASE_URL`: optional, defaults to local SQLite. For managed Postgres use a SQLAlchemy URL.
- Python runtime: pinned in `.python-version` so hosts such as Render do not default to Python 3.14.

Example PostgreSQL URL:

```text
postgresql://username:password@host:5432/database_name
```

## Deployment command

Use the Procfile command or configure the platform start command as:

```bash
gunicorn wsgi:app
```

## Render note

If Render was previously trying to build with Python 3.14, redeploy after pulling the latest commit. This repository now pins Python `3.12.6` and uses a `psycopg` version that has compatible binary wheels.

## Industry-grade features

| Feature | Details |
|---------|---------|
| **Session management** | Flask-Login — `login_user` / `logout_user` / `current_user` |
| **Rate limiting** | Flask-Limiter — 10 requests/minute on `/auth/register` and `/auth/login` |
| **CSRF protection** | Flask-WTF `CSRFProtect` applied globally; all forms carry a token |
| **Security headers** | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` on every response |
| **Structured logging** | stdlib `logging` — requests and auth events emitted at INFO/WARNING level |
| **Error pages** | Custom 404 and 500 handlers with branded templates |
| **Health endpoint** | `GET /health` returns `{"status":"ok"}` — suitable for load-balancer checks |
| **Password policy** | Min 8 chars, must contain uppercase, lowercase, and a digit |
| **Open-redirect guard** | Login `next` parameter is validated to only allow same-origin redirects |
| **DB error handling** | `try/except` + `db.session.rollback()` in register; 500 handler also rolls back |
| **Automated tests** | 24 pytest tests covering routes, auth flows, validation, and security headers |
| **CI pipeline** | GitHub Actions workflow runs tests on every push/PR to `main` |

## Notes

- SQLite is fine for quick demos. Use Postgres or another managed database for real deployment.
- `db.create_all()` runs automatically on startup for this small project. For larger apps, switch to migrations.
