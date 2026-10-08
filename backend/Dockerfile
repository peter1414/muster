FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_APP="muster:create_app()"
ENV PORT=8000
EXPOSE 8000

# Run migrations then start gunicorn. `flask db upgrade` is a no-op safe to
# run on every boot once migrations exist (see README for first-time setup).
CMD ["sh", "-c", "flask db upgrade || true; gunicorn 'muster:create_app()' --bind 0.0.0.0:${PORT} --workers 3 --timeout 60"]
