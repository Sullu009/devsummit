# Build context: repository root (see docker-compose.yml)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY shared/common /shared/common
COPY services/event-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/event-service/ .

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
