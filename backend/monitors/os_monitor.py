import psutil
import time

def get_os_metrics():
    """
    Returns a list: [CPU_Usage_%, RAM_Usage_%, Disk_Read_Speed_MBps]
    """
    try:
        # 1. Get initial disk counter
        io_start = psutil.disk_io_counters()
        
        # 2. Get CPU usage (this blocks for 1 second)
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 3. Get RAM usage
        ram_usage = psutil.virtual_memory().percent
        
        # 4. Get final disk counter and calculate difference
        io_end = psutil.disk_io_counters()
        
        # Calculate bytes read during that 1 second
        read_bytes = io_end.read_bytes - io_start.read_bytes
        
        # Convert bytes to Megabytes (MB)
        read_speed_mb = read_bytes / (1024 * 1024)
        
        return [cpu_usage, ram_usage, round(read_speed_mb, 2)]

    except Exception as e:
        print(f"Error fetching OS metrics: {e}")
        return [0, 0, 0]

# Test the function if run directly
if __name__ == "__main__":
    print("Collecting OS Data (Wait 1 sec)...")
    print(f"Metrics [CPU%, RAM%, Disk MB/s]: {get_os_metrics()}")