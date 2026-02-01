import os_monitor
import db_monitor
import algo_monitor

print("--- SYSTEM HEALTH MONITOR DIAGNOSTICS ---")

# 1. Check OS
print("1. Checking OS Metrics (Wait 1 sec)...")
os_data = os_monitor.get_os_metrics()
print(f"   [CPU: {os_data[0]}%] [RAM: {os_data[1]}%] [Disk Read: {os_data[2]} MB/s]")

# 2. Check Database
print("\n2. Checking Database Metrics...")
db_data = db_monitor.get_db_metrics()
print(f"   Active Connections: {db_data}")

# 3. Check Algorithm
print("\n3. Checking Algorithm Performance...")
algo_time = algo_monitor.run_dummy_algorithm()
print(f"   Execution Time: {algo_time} ms")

print("\n--- DIAGNOSTICS COMPLETE ---")