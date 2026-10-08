# Build the React frontend.
FROM node:24-bookworm-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# Run Django and serve the compiled frontend.
FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=False

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY scripts/start-production.sh ./scripts/start-production.sh
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

WORKDIR /app/backend

# Collect static assets without requiring the production database.
# The temporary SQLite URL is scoped to this build command only.
RUN DJANGO_SECRET_KEY=build-only-not-for-production \
    DATABASE_URL=sqlite:///:memory: \
    python manage.py collectstatic --noinput

# Run the application as a non-root user.
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "/app/scripts/start-production.sh"]
