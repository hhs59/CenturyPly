FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/backend/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

COPY backend/app /app/backend/app
COPY backend/docker-entrypoint.sh /app/docker-entrypoint.sh
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
