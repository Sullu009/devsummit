# Build context: repository root (see docker-compose.yml)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY shared/common /shared/common
COPY api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api-gateway/ .

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
