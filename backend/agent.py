"""
Remote monitoring agent — run this on any machine you want to monitor.
It collects system metrics and POSTs them to the main server every INTERVAL seconds.

Usage:
    python agent.py --server http://<YOUR_IP>:8000 --name "Friend Laptop"
"""
import argparse
import time
import socket
import psutil
import requests

INTERVAL = 5  # seconds between reports


def collect():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": mem.percent,
        "disk_percent": disk.percent,
        "net_sent_mb": round(net.bytes_sent / 1024 / 1024, 2),
        "net_recv_mb": round(net.bytes_recv / 1024 / 1024, 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="Main server URL")
    parser.add_argument("--name", default=socket.gethostname(), help="Agent display name")
    args = parser.parse_args()

    url = f"{args.server}/api/remote-metrics"
    print(f"Agent '{args.name}' → {url}  (every {INTERVAL}s)")

    while True:
        try:
            payload = {"agent_name": args.name, **collect()}
            requests.post(url, json=payload, timeout=5)
            print(f"[{time.strftime('%H:%M:%S')}] sent: CPU={payload['cpu']}%  RAM={payload['ram']}%")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] send failed: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
