"""
Task Manager–style performance metrics: CPU, Memory, Disk, Network, GPU, Uptime.
Uses psutil; GPU uses pynvml if available (NVIDIA).
"""
import platform
import time
from typing import Any

import psutil

# Optional: NVIDIA GPU via pynvml
_pynvml = None
try:
    import pynvml
    pynvml.nvmlInit()
    _pynvml = pynvml
except Exception:
    pass


# Cached process/thread count (expensive on Windows). Refresh every 5 sec.
_cpu_counts_cache: dict[str, Any] = {"processes": 0, "threads": 0, "ts": 0.0}
_CPU_COUNTS_TTL = 5.0


def _cpu_metrics() -> dict[str, Any]:
    freq = psutil.cpu_freq()
    # Fast path: process count via pids(); thread count cached to avoid 1–3s lag every request
    now = time.time()
    if now - _cpu_counts_cache["ts"] >= _CPU_COUNTS_TTL:
        process_count = len(psutil.pids())
        thread_count = 0
        try:
            for p in psutil.process_iter(["num_threads"], ad_value=None):
                try:
                    thread_count += p.info.get("num_threads") or 0
                except (psutil.NoSuchProcess, TypeError):
                    pass
        except Exception:
            pass
        _cpu_counts_cache["processes"] = process_count
        _cpu_counts_cache["threads"] = thread_count
        _cpu_counts_cache["ts"] = now
    else:
        process_count = _cpu_counts_cache["processes"]
        thread_count = _cpu_counts_cache["threads"]
    return {
        "percent": round(psutil.cpu_percent(interval=0.05), 1),  # 50ms for snappier response
        "frequency_mhz": round(freq.current, 0) if freq else 0,
        "frequency_ghz": round((freq.current or 0) / 1000, 2),
        "base_speed_mhz": round(freq.min or 0, 0),
        "base_speed_ghz": round((freq.min or 0) / 1000, 2),
        "processes": process_count,
        "threads": thread_count,
        "cores": psutil.cpu_count(logical=False) or 0,
        "logical_processors": psutil.cpu_count() or 0,
    }


def _memory_metrics() -> dict[str, Any]:
    v = psutil.virtual_memory()
    return {
        "percent": round(v.percent, 1),
        "used_gb": round(v.used / (1024**3), 2),
        "total_gb": round(v.total / (1024**3), 2),
        "available_gb": round(v.available / (1024**3), 2),
    }


def _disk_metrics() -> list[dict[str, Any]]:
    result = []
    try:
        # Partition-level disk usage and I/O
        for part in psutil.disk_partitions(all=False):
            if "fixed" in part.opts.lower() or (platform.system() == "Windows" and "cdrom" not in part.fstype.lower()):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    result.append({
                        "name": part.device if platform.system() == "Windows" else part.mountpoint,
                        "mountpoint": part.mountpoint,
                        "percent": round(usage.percent, 1),
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "type_label": "SSD (NVMe)" if "nvme" in (part.device or "").lower() else "Disk",
                    })
                except (PermissionError, OSError):
                    continue
    except Exception:
        pass
    if not result:
        # Fallback: system-wide disk
        io = psutil.disk_io_counters()
        result = [{
            "name": "C:",
            "mountpoint": "/",
            "percent": 0,
            "total_gb": 0,
            "used_gb": 0,
            "free_gb": 0,
            "type_label": "Disk",
        }]
    return result


def _disk_io_snapshot() -> dict[str, float]:
    """Current disk I/O (bytes read/write). Call twice with delay to get rates."""
    c = psutil.disk_io_counters()
    if not c:
        return {"read_bytes": 0, "write_bytes": 0}
    return {"read_bytes": c.read_bytes, "write_bytes": c.write_bytes}


# Network interfaces to hide from the Performance view
_NETWORK_SKIP_NAMES = frozenset({
    "ethernet",
    "local area connection",
    "local area connection 2",
})


def _network_metrics() -> list[dict[str, Any]]:
    by_name = {}
    try:
        for name, counters in psutil.net_io_counters(pernic=True).items():
            if not name or name.startswith("Loopback"):
                continue
            name_lower = name.strip().lower()
            if name_lower in _NETWORK_SKIP_NAMES:
                continue
            by_name[name] = {
                "name": name,
                "send_bytes": counters.bytes_sent,
                "recv_bytes": counters.bytes_recv,
            }
    except Exception:
        pass
    return list(by_name.values())


def _gpu_metrics() -> dict[str, Any] | None:
    if not _pynvml:
        return None
    try:
        handle = _pynvml.nvmlDeviceGetHandleByIndex(0)
        name = _pynvml.nvmlDeviceGetName(handle)
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="replace")
        util = _pynvml.nvmlDeviceGetUtilizationRates(handle)
        return {
            "name": name,
            "utilization_percent": util.gpu,
            "memory_used_mb": _pynvml.nvmlDeviceGetMemoryInfo(handle).used // (1024 * 1024),
            "memory_total_mb": _pynvml.nvmlDeviceGetMemoryInfo(handle).total // (1024 * 1024),
        }
    except Exception:
        return None


def _uptime_seconds() -> float:
    return time.time() - psutil.boot_time()


def get_performance_snapshot(
    *,
    disk_io_prev: dict[str, float] | None = None,
    disk_io_interval_sec: float = 1.0,
    network_prev: list[dict[str, Any]] | None = None,
    network_interval_sec: float = 1.0,
) -> dict[str, Any]:
    """
    One-shot snapshot of all performance metrics.
    Pass disk_io_prev / network_prev from previous call to get rates (MB/s, Kbps).
    """
    cpu = _cpu_metrics()
    memory = _memory_metrics()
    disks = _disk_metrics()
    networks = _network_metrics()
    gpu = _gpu_metrics()
    uptime_sec = _uptime_seconds()

    # Disk I/O rates
    io_now = _disk_io_snapshot()
    disk_read_mb_s = 0.0
    disk_write_mb_s = 0.0
    if disk_io_prev and disk_io_interval_sec > 0:
        disk_read_mb_s = (io_now["read_bytes"] - disk_io_prev.get("read_bytes", 0)) / (1024 * 1024 * disk_io_interval_sec)
        disk_write_mb_s = (io_now["write_bytes"] - disk_io_prev.get("write_bytes", 0)) / (1024 * 1024 * disk_io_interval_sec)
        disk_read_mb_s = max(0, round(disk_read_mb_s, 2))
        disk_write_mb_s = max(0, round(disk_write_mb_s, 2))

    # Network rates (Kbps) from previous snapshot
    prev_by_name = {n["name"]: n for n in (network_prev or [])}
    net_out = []
    for n in networks:
        name = n["name"]
        send_kbps = 0
        recv_kbps = 0
        if name in prev_by_name and network_interval_sec > 0:
            p = prev_by_name[name]
            send_kbps = int((n["send_bytes"] - p.get("send_bytes", 0)) * 8 / (1024 * network_interval_sec))
            recv_kbps = int((n["recv_bytes"] - p.get("recv_bytes", 0)) * 8 / (1024 * network_interval_sec))
            send_kbps = max(0, send_kbps)
            recv_kbps = max(0, recv_kbps)
        net_out.append({"name": name, "send_kbps": send_kbps, "recv_kbps": recv_kbps})
    # Sort: put Wi-Fi and Ethernet first
    net_out.sort(key=lambda x: (0 if "wi" in x["name"].lower() or "wlan" in x["name"].lower() else 1, 0 if "eth" in x["name"].lower() else 1, x["name"]))

    return {
        "cpu": cpu,
        "memory": memory,
        "disks": disks,
        "disk_io": {
            "read_mb_s": disk_read_mb_s,
            "write_mb_s": disk_write_mb_s,
        },
        "network": net_out,
        "network_raw": networks,
        "gpu": gpu,
        "uptime_seconds": round(uptime_sec, 0),
        "uptime_formatted": _format_uptime(uptime_sec),
    }


def _format_uptime(seconds: float) -> str:
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if d > 0:
        return f"{d}:{h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    import json
    prev = _disk_io_snapshot()
    time.sleep(0.5)
    snap = get_performance_snapshot(disk_io_prev=prev, disk_io_interval_sec=0.5)
    # Remove raw for print
    snap.pop("network_raw", None)
    print(json.dumps(snap, indent=2))
