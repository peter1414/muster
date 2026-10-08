# Muster

A training log that scores every workout against the real selection standards — minimum, competitive, and max lines for the Navy PST (push-ups, sit-ups, pull-ups, 1.5-mile run, 500-yd swim). Built for NSW/SOAS, BUD/S, and tactical PFT prep, and used by the RPI SpecWar/Special Operations Club to log training and benchmark members.

Built by Peter Kelly (RPI, Computer & Systems Engineering).

## What's here

| Folder | What it is |
|---|---|
| `backend/` | Flask JSON API — JWT auth, training-log CRUD with per-user ownership scoping, pagination, tiered standards scoring, SQLAlchemy + Alembic migrations, Dockerfile, and a 42-test pytest suite |
| `mobile/` | Expo / React Native (TypeScript) client — login/register, dashboard with per-event progress against each tier, log/edit entries, history, settings |
| `prototype/` | The original single-file Flask + Jinja2 web app (multi-user accounts, daily log, standards dashboard) that the API grew out of |
| `docs/` | Privacy policy and app-store listing drafts |

## Tech

Python · Flask · SQLAlchemy · Alembic · JWT · pytest · Docker · TypeScript · React Native / Expo

## Run it

See `backend/README.md` for the API (local dev + tests) and `mobile/README.md` for the app. The prototype runs with:

```bash
cd prototype
pip install -r requirements.txt
python app.py   # http://127.0.0.1:5000
```
