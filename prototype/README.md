# Muster — Training Log MVP

A working Flask app for tracking PST/PFT training against selection standards.
This is the Stage 2 build from the MVP spec: real accounts, a daily log, and a
dashboard that shows exactly where you stand against the minimum / competitive
/ max lines.

## Run it locally

```bash
cd muster_app
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**, create an account, and start logging.

The database (`muster.db`) is created automatically on first run — it's a
local SQLite file, nothing to configure.

## What's built

- **Accounts** — register/login/logout, passwords hashed with Werkzeug (never stored in plain text).
- **Log entry** — log any of 5 events (push-ups, sit-ups, pull-ups, 1.5-mile run, 500m swim). Reps are entered as whole numbers; timed events accept `mm:ss`.
- **Dashboard** — your most recent number for each event, shown against the standard's min/competitive/max lines with a progress bar and a tier tag (below / min / competitive / max).
- **History** — a full log of every entry you've ever submitted, with notes.

## Editing the standards

All standard lines live in one place at the top of `app.py`:

```python
STANDARDS = {
    "pushups": {"label": "Push-ups (2 min)", "unit": "reps",
                "min": 50, "competitive": 80, "max": 100, "lower_better": False},
    ...
}
```

Swap in the real, sourced standards for whichever pipeline you're building
this for (SOAS, BUD/S, SFAS, etc.) before you show this to anyone. The
placeholder numbers are close to public PST ranges but haven't been verified
against a current, official source.

## Known limitations (by design — this is an MVP)

- **SECRET_KEY is a placeholder.** Before deploying anywhere real, set it via
  an environment variable, not a hardcoded string in `app.py`.
- **No password reset flow yet.** Fine for you and a small early-access group;
  add this before opening signups publicly.
- **SQLite, single file.** Perfectly fine for dozens of early users. If this
  gets real traction, migrate to Postgres before scaling past a small cohort.
- **No charts yet.** The dashboard shows your latest number, not a trend line
  over time. That's the natural next feature once the core loop (log → see
  standard → log again) is validated.

## Suggested next build steps, in order

1. **Trend charts** — a simple line chart per event using the history data you're already storing (Chart.js is easy to drop into the dashboard template).
2. **Deploy it** — Render or Railway both have free tiers that work well for a small Flask + SQLite app. This turns it from "runs on my laptop" into a real link you can send people.
3. **Payments** — gate account creation behind a Stripe or Gumroad purchase link once you're ready to charge, per the monetization plan in the MVP spec.
4. **Second pipeline track** — once one track (e.g. SOAS) is validated, duplicate the standards dict for a second pipeline (SFAS, PJ/CCT) to prove the model generalizes.
