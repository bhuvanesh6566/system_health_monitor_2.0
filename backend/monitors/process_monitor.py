"""
Task Manager–style process list: per-process CPU, Memory, Disk, (Network placeholder).
Uses psutil; disk I/O rate requires two snapshots (handled by API).
"""
from typing import Any

import psutil


def get_processes_snapshot(
    *,
    io_prev: dict[int, dict[str, Any]] | None = None,
    interval_sec: float = 1.0,
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """
    Returns (list of process dicts, current io_by_pid for next call).
    Each process: name, pid, cpu_percent, memory_mb, disk_mb_s (read+write rate), count=1.
    Group by name is done in API or frontend; here we return one row per process.
    """
    result = []
    io_now: dict[int, dict[str, Any]] = {}

    try:
        for p in psutil.process_iter(["pid", "name", "memory_info", "io_counters"], ad_value=None):
            try:
                pid = p.info.get("pid")
                if pid is None:
                    continue
                name = p.info.get("name") or "Unknown"
                if not name.strip():
                    name = "Unknown"

                # CPU (instant; first call may be 0)
                try:
                    cpu = p.cpu_percent()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cpu = 0.0

                # Memory MB (RSS)
                mem_mb = 0.0
                try:
                    mem = p.info.get("memory_info")
                    if mem:
                        mem_mb = round(mem.rss / (1024 * 1024), 1)
                except (TypeError, AttributeError):
                    pass

                # Disk I/O rate from previous snapshot
                disk_mb_s = 0.0
                try:
                    io = p.info.get("io_counters")
                    if io is not None:
                        io_now[pid] = {"read": io.read_bytes, "write": io.write_bytes}
                        if io_prev and pid in io_prev and interval_sec > 0:
                            prev = io_prev[pid]
                            r = (io.read_bytes - prev.get("read", 0)) / (1024 * 1024 * interval_sec)
                            w = (io.write_bytes - prev.get("write", 0)) / (1024 * 1024 * interval_sec)
                            disk_mb_s = round(max(0, r + w), 2)
                except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                    pass

                # Executable path (for app icon); can be None if access denied
                exe_path = None
                try:
                    exe_path = p.exe()
                except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                    pass

                result.append({
                    "pid": pid,
                    "name": name.strip(),
                    "exe_path": exe_path,
                    "cpu_percent": round(cpu, 1),
                    "memory_mb": mem_mb,
                    "disk_mb_s": disk_mb_s,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError, KeyError):
                continue
    except Exception:
        pass

    return result, io_now


def get_system_summary() -> dict[str, Any]:
    """Overall CPU, Memory, Disk, Network (percent) for the summary bar."""
    try:
        cpu = psutil.cpu_percent(interval=0.05)
        mem = psutil.virtual_memory()
        disk_pct = 0
        try:
            for part in psutil.disk_partitions(all=False):
                if part.fstype and "fixed" in (part.opts or "").lower():
                    disk_pct = psutil.disk_usage(part.mountpoint).percent
                    break
        except Exception:
            pass
        return {
            "cpu_percent": round(cpu, 1),
            "memory_percent": round(mem.percent, 1),
            "disk_percent": round(disk_pct, 1),
            "network_percent": 0,
        }
    except Exception:
        return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0, "network_percent": 0}
