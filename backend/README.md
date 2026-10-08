# Muster backend (API)

JSON API for the Muster training-log app. This replaces the original
single-file Flask app's server-rendered HTML routes with a token-authenticated
API a native/React Native client can talk to. The original file is kept at
`app_original.py` for reference — nothing in this package imports it.

## Local dev

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env if you want, defaults work with zero setup (SQLite, dev secret key)

export FLASK_APP="muster:create_app()"
export FLASK_ENV=development
flask db upgrade      # creates instance/muster.db and applies migrations
python run.py          # http://127.0.0.1:5000
```

Health check: `GET /healthz` -> `{"status": "ok"}`

## Running tests

```bash
source venv/bin/activate
export SECRET_KEY=test PYTHONPATH=.
python -m pytest tests/ -v
```

42 tests covering auth, entry CRUD, ownership scoping, pagination, and the
standards/tier calculation logic. All passing as of the last run in this repo.

## API overview

All `/api/*` routes except `/api/standards` require `Authorization: Bearer <access_token>`.

| Method | Path                      | Notes                                    |
|--------|---------------------------|-------------------------------------------|
| POST   | /api/auth/register        | -> access_token, refresh_token, user      |
| POST   | /api/auth/login           |                                            |
| POST   | /api/auth/refresh         | needs refresh_token                       |
| POST   | /api/auth/forgot-password | see "Email" below                         |
| POST   | /api/auth/reset-password  |                                            |
| DELETE | /api/auth/account         | required by App Store Guideline 5.1.1(v)  |
| GET    | /api/me                   |                                            |
| GET    | /api/standards            | public, no auth — static reference data   |
| GET    | /api/dashboard            | latest entry + tier per exercise          |
| GET    | /api/entries              | `?page=&per_page=&exercise=`              |
| POST   | /api/entries              |                                            |
| PUT    | /api/entries/<id>         | partial update, owner-scoped              |
| DELETE | /api/entries/<id>         | owner-scoped                              |

## Before this goes to production

- [ ] Set a real `SECRET_KEY` (32+ random bytes) as an env var/secret on the host — the app **refuses to start** in `FLASK_ENV=production` without one.
- [ ] Point `DATABASE_URL` at a real Postgres instance. SQLite is dev-only.
- [ ] Lock down `CORS_ORIGINS` to your actual app's origin(s) instead of `*`.
- [ ] **Email**: `POST /api/auth/forgot-password` doesn't send email yet — no provider is wired up. While `EMAIL_BACKEND` is unset, it returns the reset token directly in the JSON response (and logs a warning) so the flow is testable. Wire up SES/SendGrid/Postmark/etc. in `muster/auth.py::forgot_password`, set `EMAIL_BACKEND`, and remove the `dev_reset_token` branch before shipping.
- [ ] Put this behind HTTPS (your host's load balancer/proxy, or a service like Render/Fly that terminates TLS for you).
- [ ] Review `Flask-Limiter`'s in-memory rate-limit storage — fine for a single instance, but switch `RATELIMIT_STORAGE_URI` to Redis if you run more than one worker/instance.

## Deploying

```bash
docker build -t muster-backend .
docker run -p 8000:8000 -e SECRET_KEY=... -e DATABASE_URL=postgresql://... muster-backend
```

The container runs `flask db upgrade` on every boot before starting gunicorn,
so schema migrations apply automatically on deploy.
