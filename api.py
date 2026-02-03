"""
Thin REST API for the AI System Monitor.
Reuses backend core: os_monitor, db_monitor, algo_monitor + health_model.pkl.
No changes to those modules—this layer only exposes HTTP endpoints.
"""
import logging
import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os_monitor
import db_monitor
import algo_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_FILE = "health_model.pkl"
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


@app.get("/api/health")
def get_health():
    """
    Returns current metrics and anomaly prediction.
    Uses backend core: os_monitor, db_monitor, algo_monitor + Isolation Forest.
    """
    try:
        model = get_model()
    except FileNotFoundError:
        return _safe_response("Model file not found. Run train_model.py first.")
    except Exception as e:
        logger.exception("Failed to load model")
        return _safe_response(f"Model load failed: {e!s}")

    try:
        os_data = os_monitor.get_os_metrics()   # [CPU, RAM, Disk]
        db_threads = db_monitor.get_db_metrics()
        algo_ms = algo_monitor.run_dummy_algorithm()
    except Exception as e:
        logger.exception("Failed to collect metrics")
        return _safe_response(f"Metrics failed: {e!s}")

    try:
        # Same feature order/names as train_model.py so sklearn doesn't warn
        X = pd.DataFrame(
            [[os_data[0], os_data[1], os_data[2], db_threads, algo_ms]],
            columns=FEATURES,
        )
        prediction = model.predict(X)[0]  # 1 = normal, -1 = anomaly
        is_healthy = bool(int(prediction) == 1)
    except Exception as e:
        logger.exception("Prediction failed")
        return _safe_response(f"Prediction failed: {e!s}")

    # Native Python types so FastAPI JSON encoder never sees numpy types
    return {
        "cpu": float(round(float(os_data[0]), 2)),
        "ram": float(round(float(os_data[1]), 2)),
        "disk_mb_s": float(os_data[2]),
        "db_threads": int(db_threads),
        "algo_ms": float(round(float(algo_ms), 2)),
        "is_healthy": is_healthy,
    }


@app.get("/api/ping")
def ping():
    return {"status": "ok", "service": "AIOps Monitor API"}
