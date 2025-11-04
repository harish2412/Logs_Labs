import logging
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from logging.handlers import RotatingFileHandler
from collections import defaultdict

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
METRICS_PATH = log_dir / "metrics.json"

METRICS = {
    "start_ts": None,              
    "levels": defaultdict(int),    
    "requests": 0,                  
    "errors": 0,                    
    "latency_ms": {              
        "count": 0,
        "sum": 0.0,
        "max": 0.0
    }
}

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = getattr(record, "request_id")
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)

class LevelCountFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "_counted", False):
            return True
        METRICS["levels"][record.levelname] += 1
        record._counted = True
        return True

def setup_logging():
    """
    Dual handlers:
      - Console (human-readable, UTC)
      - Rotating file (JSON, UTC)
    Level via env: LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL (default INFO)
    """
    logger = logging.getLogger("MLOps_Logger")
    if logger.handlers:
        logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
        return logger

    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    logger.addFilter(LevelCountFilter())

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_fmt = logging.Formatter(
        "%(asctime)sZ - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    import time as _t
    console_fmt.converter = _t.gmtime
    console_handler.setFormatter(console_fmt)

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1_000_000,   
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    if METRICS["start_ts"] is None:
        METRICS["start_ts"] = time.time()

    return logger

def record_latency_ms(ms: float):
    s = METRICS["latency_ms"]
    s["count"] += 1
    s["sum"] += ms
    if ms > s["max"]:
        s["max"] = ms

def write_metrics():
    levels = dict(METRICS["levels"])
    out = {
        "uptime_sec": round(time.time() - METRICS["start_ts"], 3) if METRICS["start_ts"] else 0.0,
        "levels": levels,
        "requests": METRICS["requests"],
        "errors": METRICS["errors"],
        "latency_ms": {
            "count": METRICS["latency_ms"]["count"],
            "avg": round(METRICS["latency_ms"]["sum"] / METRICS["latency_ms"]["count"], 3) if METRICS["latency_ms"]["count"] else 0.0,
            "max": round(METRICS["latency_ms"]["max"], 3),
        },
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

def demo_logging():
    logger = setup_logging()

    logger.info("Application started - Logging Lab with metrics")
    logger.debug("This is a debug message with detailed information")
    logger.warning("This is a warning - something might need attention")
    logger.error("This is an error message")

    try:
        data = [1, 2, 3, 4, 5]
        result = sum(data) / len(data)
        logger.info(f"Data processing completed. Average: {result}")
    except Exception:
        logger.exception("An error occurred during data processing")

    try:
        _ = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division by zero error caught and logged")

    write_metrics()
    logger.info("Application finished successfully")

if __name__ == "__main__":
    demo_logging()
