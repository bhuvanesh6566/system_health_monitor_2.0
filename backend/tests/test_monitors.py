import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

print("--- Testing os_monitor ---")
try:
    import os_monitor
    print(os_monitor.get_os_metrics())
except Exception as e:
    print(f"os_monitor failed: {e}")

print("\n--- Testing performance_monitor ---")
try:
    import performance_monitor
    print(performance_monitor.get_performance_snapshot())
except Exception as e:
    print(f"performance_monitor failed: {e}")

print("\n--- Testing process_monitor ---")
try:
    import process_monitor
    print(process_monitor.get_system_summary())
    procs, _ = process_monitor.get_processes_snapshot()
    print(f"Captured {len(procs)} processes")
except Exception as e:
    print(f"process_monitor failed: {e}")

print("\n--- Done ---")
