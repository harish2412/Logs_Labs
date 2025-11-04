from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import uuid
import time

from log_demo import setup_logging, METRICS, record_latency_ms, write_metrics

app = FastAPI(title="Logging Lab API")
logger = setup_logging()

@app.middleware("http")
async def add_request_logging(request: Request, call_next):
    
    rid = str(uuid.uuid4())
    path = request.url.path
    start = time.perf_counter()

    logger.info(f"➡️  {path} incoming", extra={"request_id": rid})
    METRICS["requests"] += 1

    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        METRICS["errors"] += 1
        logger.exception(f"  {path} unhandled error", extra={"request_id": rid})
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        record_latency_ms(elapsed_ms)
        logger.info(
            f"⬅️  {path} completed {status} in {elapsed_ms:.2f} ms",
            extra={"request_id": rid}
        )
        write_metrics()

    if status >= 400:
        METRICS["errors"] += 1

    return response

@app.get("/", include_in_schema=False)
def root():
    """Redirect root URL to Swagger UI (/docs)"""
    logger.info("Root accessed — redirecting to /docs")
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Avoid 404 spam for browser favicon requests"""
    return JSONResponse(content={}, status_code=204)

@app.get("/health")
def health():
    logger.info("Health check OK")
    return {"status": "ok"}

@app.get("/divide")
def divide(a: float, b: float):
    try:
        result = a / b
        logger.info(f"Division result = {result}")
        return {"a": a, "b": b, "result": result}
    except ZeroDivisionError:
        logger.exception("Division by zero")
        return JSONResponse(content={"error": "Cannot divide by zero"}, status_code=400)

@app.get("/metrics")
def metrics():
    """Serve current metrics snapshot"""
    write_metrics()
    return {
        "metrics": METRICS,
        "hint": "See logs/metrics.json for formatted summary"
    }
