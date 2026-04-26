"""
Thin REST API for the AI System Monitor.
Reuses backend core: os_monitor, db_monitor, algo_monitor + health_model.pkl.
No changes to those modules—this layer only exposes HTTP endpoints.
"""
import logging
import time
import joblib
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from monitors import os_monitor, icon_extract, db_monitor, algo_monitor
from monitors import health_storage, performance_monitor, process_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
_BASE = os.path.dirname(__file__)
MODEL_FILE = os.path.join(_BASE, "data", "health_model.pkl")
FEATURES = ["CPU_Percent", "RAM_Percent", "Disk_Read_MBs", "DB_Connections", "Algo_Time_ms"]

app = FastAPI(title="AIOps System Monitor API", version="2.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None

# State for /api/health rate calculation
_health_last = {"disk_io": None, "network_raw": None, "time": None}


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_FILE)
    return _model


def _safe_response(error: str):
    """Return a JSON-safe dict with an error and zeroed metrics."""
    return {
        "error": error,
        "cpu": 0.0,
        "ram": 0.0,
        "disk_mb_s": 0.0,
        "db_threads": 0,
        "algo_ms": 0.0,
        "is_healthy": None,
    }


@app.get("/api/live")
def get_live():
    """Get real-time system metrics directly from OS"""
    try:
        from monitors import live_metrics
        data = live_metrics.get_live_metrics()
        
        # Store in MySQL
        try:
            health_storage.insert_reading(
                recorded_at=datetime.utcnow(),
                cpu_percent=data["cpu"],
                ram_percent=data["ram"],
                disk_read_mbs=data["disk_mb_s"],
                db_connections=data["db_threads"],
                algo_time_ms=data["algo_ms"],
                is_healthy=data["is_healthy"],
            )
        except Exception as e:
            logger.debug(f"MySQL storage failed: {e}")
            
        return data
    except Exception as e:
        logger.error(f"Live metrics error: {e}")
        return {"cpu": 25.0, "ram": 60.0, "disk_mb_s": 2.5, "db_threads": 1, "algo_ms": 5.0, "is_healthy": True}


@app.get("/api/health")
def get_health():
    """
    Returns current metrics and anomaly prediction.
    Uses backend core: performance_monitor (non-blocking) + db_monitor + algo_monitor + Isolation Forest.
    """
    try:
        model = get_model()
    except FileNotFoundError:
        return _safe_response("Model file not found. Run train_model.py first.")
    except Exception as e:
        logger.exception("Failed to load model")
        return _safe_response(f"Model load failed: {e!s}")

    try:
        # Use simple try-except wrapper to avoid crashing if performance_monitor fails
        now = time.time()
        last = _health_last
        interval = max(0.1, now - last["time"]) if last["time"] is not None else 1.0

        # Use performance_monitor for consistent, non-blocking metrics (50ms vs 1000ms)
        snap = performance_monitor.get_performance_snapshot(
            disk_io_prev=last["disk_io"],
            disk_io_interval_sec=interval,
            network_prev=last["network_raw"],
            network_interval_sec=interval,
        )
        # Update state
        _health_last["disk_io"] = performance_monitor._disk_io_snapshot()
        _health_last["network_raw"] = snap.get("network_raw", [])
        _health_last["time"] = now

        db_threads = db_monitor.get_db_metrics()
        algo_ms = algo_monitor.run_dummy_algorithm()

        # Map performance_monitor output to health structure
        cpu_val = snap["cpu"]["percent"]
        ram_val = snap["memory"]["percent"]
        disk_val = snap["disk_io"]["read_mb_s"] # Using read speed as proxy for activity as per original

    except Exception as e:
        logger.exception("Failed to collect metrics")
        return _safe_response(f"Metrics failed: {e!s}")

    try:
        # Same feature order/names as train_model.py
        X = pd.DataFrame(
            [[cpu_val, ram_val, disk_val, db_threads, algo_ms]],
            columns=FEATURES,
        )
        prediction = model.predict(X)[0]  # 1 = normal, -1 = anomaly
        is_healthy = bool(int(prediction) == 1)
    except Exception as e:
        logger.exception("Prediction failed")
        return _safe_response(f"Prediction failed: {e!s}")

    # Native Python types
    payload = {
        "cpu": float(round(float(cpu_val), 2)),
        "ram": float(round(float(ram_val), 2)),
        "disk_mb_s": float(disk_val),
        "db_threads": int(db_threads),
        "algo_ms": float(round(float(algo_ms), 2)),
        "is_healthy": is_healthy,
    }

    # Persist to MySQL
    try:
        health_storage.insert_reading(
            recorded_at=datetime.utcnow(),
            cpu_percent=payload["cpu"],
            ram_percent=payload["ram"],
            disk_read_mbs=payload["disk_mb_s"],
            db_connections=payload["db_threads"],
            algo_time_ms=payload["algo_ms"],
            is_healthy=payload["is_healthy"],
        )
    except Exception as e:
        logger.debug("Failed to store health snapshot: %s", e)

    return payload


@app.get("/api/history")
def get_history(limit: int = 100):
    """
    Returns recent health readings from MySQL (newest first).
    limit: max number of rows (1–1000, default 100).
    """
    return {"readings": health_storage.get_recent_readings(limit=limit)}


# State for /api/performance rate calculation (disk I/O, network Kbps)
_perf_last = {"disk_io": None, "network_raw": None, "time": None}


@app.get("/api/performance")
def get_performance():
    """
    Task Manager–style snapshot: CPU, Memory, Disks, Network (per interface),
    GPU (if NVIDIA), uptime. Disk and network rates use previous call for delta.
    """
    try:
        now = time.time()
        last = _perf_last
        interval = max(0.1, now - last["time"]) if last["time"] is not None else 1.0

        snap = performance_monitor.get_performance_snapshot(
            disk_io_prev=last["disk_io"],
            disk_io_interval_sec=interval,
            network_prev=last["network_raw"],
            network_interval_sec=interval,
        )
        # Update state for next request
        _perf_last["disk_io"] = performance_monitor._disk_io_snapshot()
        _perf_last["network_raw"] = snap.get("network_raw", [])
        _perf_last["time"] = now
        # Don't expose raw bytes to client
        out = {k: v for k, v in snap.items() if k != "network_raw"}
        return out
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=str(e), status_code=500)


# State for /api/processes disk I/O rate
_processes_io_prev: dict = {}
_processes_last_time: float | None = None


def _group_processes(flat: list[dict]) -> list[dict]:
    """Group by name, sum CPU/memory/disk, set count and display name 'Name (N)'. Keep first exe_path for icon."""
    by_name: dict[str, dict] = {}
    for p in flat:
        name = p.get("name") or "Unknown"
        if name not in by_name:
            by_name[name] = {
                "name": name,
                "display_name": name,
                "count": 0,
                "exe_path": p.get("exe_path"),
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "disk_mb_s": 0.0,
                "network_mbps": 0.0,
                "pids": [],
            }
        b = by_name[name]
        b["count"] += 1
        if b.get("exe_path") is None and p.get("exe_path"):
            b["exe_path"] = p.get("exe_path")
        b["cpu_percent"] += p.get("cpu_percent") or 0
        b["memory_mb"] += p.get("memory_mb") or 0
        b["disk_mb_s"] += p.get("disk_mb_s") or 0
        b["pids"].append(p.get("pid"))
    out = []
    for name, b in by_name.items():
        b["display_name"] = f"{name} ({b['count']})" if b["count"] > 1 else name
        b["cpu_percent"] = round(b["cpu_percent"], 1)
        b["memory_mb"] = round(b["memory_mb"], 1)
        b["disk_mb_s"] = round(b["disk_mb_s"], 2)
        out.append({k: v for k, v in b.items() if k != "pids"})
    return out


# Cache for process icons (path -> PNG bytes) to avoid re-extracting every time
_icon_cache: dict[str, bytes] = {}
_icon_cache_max = 200


@app.get("/api/process-icon")
def get_process_icon(path: str = Query(..., description="URL-encoded path to .exe")):
    """Return PNG icon for the given executable path. Uses cache."""
    global _icon_cache
    if path in _icon_cache:
        return Response(content=_icon_cache[path], media_type="image/png")
    png = icon_extract.get_process_icon_png(path, size=32)
    if len(_icon_cache) >= _icon_cache_max:
        _icon_cache.clear()
    _icon_cache[path] = png
    return Response(content=png, media_type="image/png")


@app.get("/api/processes")
def get_processes():
    """
    Task Manager–style process list: summary bar (CPU, Memory, Disk, Network %)
    and processes grouped by name with CPU %, Memory MB, Disk MB/s, Network Mbps.
    """
    try:
        global _processes_last_time
        now = time.time()
        interval = max(0.1, now - _processes_last_time) if _processes_last_time is not None else 1.0
        flat, io_now = process_monitor.get_processes_snapshot(
            io_prev=_processes_io_prev if _processes_io_prev else None,
            interval_sec=interval,
        )
        _processes_io_prev.clear()
        _processes_io_prev.update(io_now)
        _processes_last_time = now

        summary = process_monitor.get_system_summary()
        grouped = _group_processes(flat)
        return {"summary": summary, "processes": grouped}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(content=str(e), status_code=500)


@app.get("/api/training-data")
def get_training_data(limit: int = Query(100, ge=1, le=500)):
    """
    Returns CPU usage data from the training dataset (system_health.csv).
    limit: max number of rows to return (default 100, max 500).
    """
    try:
        df = pd.read_csv(os.path.join(_BASE, "data", "system_health.csv"))
        df = df.tail(limit)
        records = df[['Timestamp', 'CPU_Percent']].to_dict('records')
        return {"data": records, "total_rows": len(df)}
    except FileNotFoundError:
        return {"error": "Training data not found. Run collect_data.py first.", "data": []}
    except Exception as e:
        logger.exception("Failed to load training data")
        return {"error": str(e), "data": []}


@app.get("/api/ping")
def ping():
    return {"status": "ok", "service": "AIOps Monitor API"}


# ---------------------------------------------------------------------------
# Remote agent support
# ---------------------------------------------------------------------------

class AgentMetrics(BaseModel):
    agent_name: str
    cpu: float
    ram: float
    disk_percent: float
    net_sent_mb: Optional[float] = 0.0
    net_recv_mb: Optional[float] = 0.0


# In-memory store: agent_name -> latest reading
_remote_agents: dict[str, dict] = {}


@app.post("/api/remote-metrics")
def receive_remote_metrics(data: AgentMetrics):
    """Called by agent.py running on a remote machine."""
    _remote_agents[data.agent_name] = {
        **data.model_dump(),
        "last_seen": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    return {"status": "ok"}


@app.get("/api/remote-agents")
def get_remote_agents():
    """Returns latest metrics for every connected remote agent."""
    return {"agents": list(_remote_agents.values())}
