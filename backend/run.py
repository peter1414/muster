"""
Local dev / plain-WSGI entrypoint.

    python run.py

For production, don't use this directly — run it behind a real WSGI
server, e.g.:

    gunicorn "muster:create_app()" --bind 0.0.0.0:8000 --workers 3

(see Dockerfile / README).
"""
import os

from muster import create_app
from muster.extensions import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # fine for dev/sqlite; use `flask db upgrade` in prod
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=app.config["DEBUG"])
