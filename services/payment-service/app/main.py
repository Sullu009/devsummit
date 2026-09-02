import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import internal, payments, revenue

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="EventSphere Payment Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    start = time.time()
    response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id
    duration_ms = int((time.time() - start) * 1000)
    logging.getLogger("eventsphere.access").info(
        "%s %s %s status=%s duration_ms=%s corr_id=%s",
        settings.service_name, request.method, request.url.path, response.status_code, duration_ms, correlation_id,
    )
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.service_name}


app.include_router(payments.router)
app.include_router(revenue.router)
app.include_router(internal.router)
