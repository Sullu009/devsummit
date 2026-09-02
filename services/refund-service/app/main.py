import logging
import threading
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import router as refunds_router
from .worker import run_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def _start_worker_thread():
    def _loop():
        while True:
            try:
                run_worker()
            except Exception:  # noqa: BLE001
                logging.getLogger("eventsphere.refund.worker").exception("Consumer crashed, restarting in 5s")
                time.sleep(5)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


@asynccontextmanager
async def lifespan(app: FastAPI):
    _start_worker_thread()
    yield


app = FastAPI(title="EventSphere Refund Service", version="1.0.0", lifespan=lifespan)

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


app.include_router(refunds_router)
