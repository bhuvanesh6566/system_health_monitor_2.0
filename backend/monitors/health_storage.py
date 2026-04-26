"""
MySQL storage for AIOps health metrics.
Uses env vars for credentials with fallback; same DB can be used for
storing readings (this module) and for db_monitor metrics (system DB).
"""
import os
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import Error as MySQLError

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Database for storing health readings (can be same host as db_monitor, different database)
def _get_config():
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "aiops_user"),
        "password": os.environ.get("MYSQL_PASSWORD", "aiops_secure_password_2026"),
        "database": os.environ.get("MYSQL_DATABASE", "aiops_monitor"),
    }


def get_connection():
    """Return a new MySQL connection for the monitor database."""
    return mysql.connector.connect(**_get_config())


def init_db() -> bool:
    """
    Create the health_readings table if it does not exist.
    Assumes the database (e.g. aiops_monitor) already exists.
    Returns True on success, False on failure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_readings (
                id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                recorded_at    DATETIME(3)     NOT NULL,
                cpu_percent    DECIMAL(6,2)   NOT NULL,
                ram_percent    DECIMAL(6,2)   NOT NULL,
                disk_read_mbs  DECIMAL(10,4)  NOT NULL,
                db_connections INT UNSIGNED   NOT NULL,
                algo_time_ms   DECIMAL(10,4)  NOT NULL,
                is_healthy     TINYINT(1)     NULL,
                created_at     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_recorded_at (recorded_at),
                INDEX idx_healthy (is_healthy)
            ) ENGINE=InnoDB
        """)
        conn.commit()
        cursor.close()
        logger.info("health_readings table ready.")
        return True
    except MySQLError as e:
        logger.exception("init_db failed: %s", e)
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def insert_reading(
    recorded_at: datetime,
    cpu_percent: float,
    ram_percent: float,
    disk_read_mbs: float,
    db_connections: int,
    algo_time_ms: float,
    is_healthy: Optional[bool] = None,
) -> bool:
    """
    Insert one health snapshot into health_readings.
    Returns True on success, False on failure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO health_readings
            (recorded_at, cpu_percent, ram_percent, disk_read_mbs, db_connections, algo_time_ms, is_healthy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                recorded_at,
                round(float(cpu_percent), 2),
                round(float(ram_percent), 2),
                round(float(disk_read_mbs), 4),
                int(db_connections),
                round(float(algo_time_ms), 4),
                1 if is_healthy is True else (0 if is_healthy is False else None),
            ),
        )
        conn.commit()
        cursor.close()
        return True
    except MySQLError as e:
        logger.warning("insert_reading failed: %s", e)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def get_recent_readings(limit: int = 100):
    """
    Fetch the most recent health readings, newest first.
    Returns list of dicts with keys: id, recorded_at, cpu_percent, ram_percent,
    disk_read_mbs, db_connections, algo_time_ms, is_healthy.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, recorded_at, cpu_percent, ram_percent, disk_read_mbs,
                   db_connections, algo_time_ms, is_healthy
            FROM health_readings
            ORDER BY recorded_at DESC
            LIMIT %s
            """,
            (max(1, min(limit, 1000)),),
        )
        rows = cursor.fetchall()
        cursor.close()
        # Convert datetime and decimal to serializable types
        out = []
        for r in rows:
            out.append({
                "id": r["id"],
                "recorded_at": r["recorded_at"].isoformat() if r["recorded_at"] else None,
                "cpu_percent": float(r["cpu_percent"]),
                "ram_percent": float(r["ram_percent"]),
                "disk_read_mbs": float(r["disk_read_mbs"]),
                "db_connections": int(r["db_connections"]),
                "algo_time_ms": float(r["algo_time_ms"]),
                "is_healthy": bool(r["is_healthy"]) if r["is_healthy"] is not None else None,
            })
        return out
    except MySQLError as e:
        logger.warning("get_recent_readings failed: %s", e)
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if init_db():
        print("Table ready.")
        ok = insert_reading(
            datetime.utcnow(), 10.5, 60.0, 1.2, 2, 5.0, is_healthy=True
        )
        print("Insert test:", "OK" if ok else "FAIL")
        print("Recent:", get_recent_readings(5))
