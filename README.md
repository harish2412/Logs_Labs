# Logging Lab – Custom JSON Logger with FastAPI

This project demonstrates how to build a structured logging and monitoring system in Python.  
It extends the professor’s starter version into a complete FastAPI application that logs every request, captures errors, and tracks runtime metrics automatically.

---

## Changes Made by Me

Compared to the professor’s starter file, the following enhancements were implemented:

- Integrated **FastAPI** with three functional endpoints (`/health`, `/divide`, `/metrics`)
- Added **middleware-based logging** to record every request with latency and status
- Built a **dual logging system** for console (human-readable) and JSON file (machine-readable) outputs
- Implemented **metrics tracking** for requests, errors, latency, and log level counts
- Configured **rotating log files** to prevent unlimited file growth
- Developed **unit tests** to validate log structure, metrics, and API behavior
- Added **root redirect (/ → /docs)** and handled **favicon** requests to avoid unnecessary 404 errors
- Improved **error handling**, returning HTTP 400 for invalid division requests

---

## Project Overview

The purpose of this lab is to demonstrate production-grade logging for real-world systems.  
Each API request is automatically logged to:

- The **console**, in a readable format for developers
- The **logs/app.log** file, in structured JSON format suitable for analysis

The system also maintains a **metrics summary (`logs/metrics.json`)**, which records:
- Total requests handled
- Error counts
- Average and maximum latency
- Log level usage (INFO, ERROR, etc.)

---

## Endpoints

| Endpoint | Description | Example Output |
|-----------|--------------|----------------|
| `/health` | Verifies API health | `{"status": "ok"}` |
| `/divide?a=10&b=2` | Demonstrates successful request logging | `{"a":10,"b":2,"result":5.0}` |
| `/divide?a=10&b=0` | Demonstrates exception handling and error logging | `{"error":"Cannot divide by zero"}` |
| `/metrics` | Displays the current metrics summary | `{ "metrics": {...} }` |
| `/docs` | Swagger UI for interactive testing | Auto-generated interface |

---

## Project Structure
```
Logging_Labs/
│
├── app.py # FastAPI application and middleware
├── log_demo.py # Logger configuration and metrics logic
├── tests/
│ └── test_lab.py # Unit tests for logging and API endpoints
├── logs/
│ ├── app.log # JSON-formatted log file
│ └── metrics.json # Metrics summary (auto-updated)
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md
```
Example Outputs:
```
Console Output (Human-Readable)
2025-11-04T04:20:10Z - MLOps_Logger - INFO - Application started - Logging Lab with metrics
2025-11-04T04:20:10Z - MLOps_Logger - WARNING - This is a warning - something might need attention
2025-11-04T04:20:10Z - MLOps_Logger - ERROR - This is an error message
2025-11-04T04:20:10Z - MLOps_Logger - INFO - Data processing completed. Average: 3.0
2025-11-04T04:20:10Z - MLOps_Logger - ERROR - Division by zero error caught and logged
```
File Output (JSON Format)
```
{"timestamp": "2025-11-04T03:54:39Z", "level": "INFO", "logger_name": "MLOps_Logger", "message": "➡️  /docs incoming", "module": "app", "function": "add_request_logging", "line_number": 20, "request_id": "765d9327-d673-4dcb-8896-3ad38f62bb0c"}
{"timestamp": "2025-11-04T03:54:39Z", "level": "INFO", "logger_name": "MLOps_Logger", "message": "⬅️  /docs completed 200 in 1.30 ms", "module": "app", "function": "add_request_logging", "line_number": 33, "request_id": "765d9327-d673-4dcb-8896-3ad38f62bb0c"}
{"timestamp": "2025-11-04T03:54:39Z", "level": "INFO", "logger_name": "MLOps_Logger", "message": "➡️  /openapi.json incoming", "module": "app", "function": "add_request_logging", "line_number": 20, "request_id": "c17939e4-c7c8-4aef-a924-4d74c5777898"}
```
Relevance to MLOps:
This project demonstrates how to embed observability and traceability into an MLOps pipeline.
Structured JSON logs enable:
  Easier debugging of data and model pipelines
  Integration with log aggregation tools (e.g., ELK, CloudWatch, Splunk)
  Automated monitoring and alerting systems
  Improved compliance and audit readiness

Harish Padmanabhan
IE 7374 – MLOps

=======
# Logs_Labs
>>>>>>> 7aeacebcd93ce41044132a6f5a199b59c8270b50
