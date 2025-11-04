import json
import io
import logging
import pathlib
import pytest
import httpx

import log_demo as ld  # import the module so we can patch paths
from log_demo import JSONFormatter, METRICS, write_metrics
from app import app


# ---------- 1) Validate JSON log schema ----------
def test_json_formatter_keys():
    formatter = JSONFormatter()
    logger = logging.getLogger("MLOps_Logger.test_json")
    # isolate this logger
    logger.handlers.clear()
    logger.propagate = False

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("test message", extra={"request_id": "abc123"})
    handler.flush()

    line = stream.getvalue().strip().splitlines()[-1]
    data = json.loads(line)

    expected = {"timestamp", "level", "logger_name", "message", "module", "function", "line_number"}
    missing = expected - set(data.keys())
    assert not missing, f"Missing keys: {missing}"
    assert data["request_id"] == "abc123"


# ---------- 2) Validate metrics file (no CWD changes) ----------
def test_write_metrics(tmp_path, monkeypatch):
    # set some counts
    METRICS["levels"]["INFO"] += 1
    METRICS["requests"] += 2
    METRICS["errors"] += 1
    METRICS["latency_ms"]["count"] = 2
    METRICS["latency_ms"]["sum"] = 100
    METRICS["latency_ms"]["max"] = 70

    # patch log_demo paths to a temp logs dir
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ld, "log_dir", logs_dir, raising=False)
    monkeypatch.setattr(ld, "METRICS_PATH", logs_dir / "metrics.json", raising=False)

    write_metrics()  # writes to tmp logs dir now

    with open(logs_dir / "metrics.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "levels" in data and "requests" in data and "errors" in data
    assert isinstance(data["levels"], dict)


# ---------- 3) Validate FastAPI endpoints using httpx ASGI transport ----------
@pytest.mark.asyncio
async def test_fastapi_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # /health should return 200
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # /divide normal case
        r = await client.get("/divide", params={"a": 10, "b": 2})
        assert r.status_code == 200
        assert "result" in r.json()

        # /divide error case (zero division) — current app returns 200 with {"error": ...}
        r = await client.get("/divide", params={"a": 10, "b": 0})
        assert r.status_code == 200  # change to 400 here if you update the endpoint to return 400
        assert "error" in r.json()

        # /metrics returns dict and is 200
        r = await client.get("/metrics")
        assert r.status_code == 200
        body = r.json()
        assert "metrics" in body
