import time
import uuid
from datetime import datetime, timezone
from collections import deque
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

# Startup time tracking for uptime_s
START_TIME = time.time()

# Prometheus counter and log tail storage
REQUEST_COUNT = 0
LOG_BUFFER = deque(maxlen=1000)  # Store up to last 1000 logs

@app.middleware("http")
async def instrumentation_middleware(request: Request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    path = request.url.path
    
    # Process request
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = 500
        raise exc
    finally:
        # Record structured log entry
        log_entry = {
            "level": "INFO" if status_code < 400 else "ERROR",
            "ts": datetime.now(timezone.utc).isoformat(),
            "path": path,
            "request_id": request_id,
            "status": status_code
        }
        LOG_BUFFER.append(log_entry)
        
    return response

@app.get("/work")
def do_work(n: int = Query(..., description="Units of work")):
    # Simulate work
    return {
        "email": "24f2007837@ds.study.iitm.ac.in",
        "done": n
    }

@app.get("/metrics")
def metrics():
    # Prometheus text format exposure for http_requests_total
    metrics_data = (
        "# HELP http_requests_total Total number of HTTP requests.\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {REQUEST_COUNT}\n"
    )
    return Response(content=metrics_data, media_type="text/plain")

@app.get("/healthz")
def healthz():
    uptime = time.time() - START_TIME
    return {
        "status": "ok",
        "uptime_s": round(uptime, 4)
    }

@app.get("/logs/tail")
def logs_tail(limit: int = Query(10, description="Number of recent logs to return")):
    logs_list = list(LOG_BUFFER)
    # Return the last N log entries
    return logs_list[-limit:]
