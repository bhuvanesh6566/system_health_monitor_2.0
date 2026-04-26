import csv
import os
import time
from datetime import datetime

import os_monitor
import db_monitor
import algo_monitor
import health_storage

# --- CONFIGURATION ---
FILE_NAME = "system_health.csv"
# We want about 30 minutes of data.
# If we check every 2 seconds: 30 mins * 60 secs / 2 = 900 rows.
ROWS_TO_COLLECT = 900  
INTERVAL_SEC = 2       

def collect_training_data():
    print(f"--- STARTING DATA COLLECTION ---")
    print(f"Target: {ROWS_TO_COLLECT} rows (approx 30 mins)")
    print(f"Saving to: {FILE_NAME}\n")

    # Check if file exists so we don't write headers twice if you restart
    file_exists = os.path.isfile(FILE_NAME)
    
    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header ONLY if it's a new file
        if not file_exists:
            writer.writerow(['Timestamp', 'CPU_Percent', 'RAM_Percent', 
                             'Disk_Read_MBs', 'DB_Connections', 'Algo_Time_ms'])

        # Loop to collect data
        for i in range(ROWS_TO_COLLECT):
            try:
                # 1. Get current timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 2. Fetch Metrics from your modules
                # Note: os_metrics returns [CPU, RAM, Disk]
                os_metrics = os_monitor.get_os_metrics() 
                db_conns = db_monitor.get_db_metrics()   
                algo_time = algo_monitor.run_dummy_algorithm() 

                # 3. Combine into one row
                row = [
                    timestamp, 
                    os_metrics[0], # CPU
                    os_metrics[1], # RAM
                    os_metrics[2], # Disk
                    db_conns, 
                    algo_time
                ]
                
                # 4. Write to CSV
                writer.writerow(row)

                # 4b. Store in MySQL (best-effort)
                try:
                    health_storage.insert_reading(
                        recorded_at=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                        cpu_percent=os_metrics[0],
                        ram_percent=os_metrics[1],
                        disk_read_mbs=os_metrics[2],
                        db_connections=db_conns,
                        algo_time_ms=algo_time,
                        is_healthy=None,
                    )
                except Exception as e:
                    print(f"MySQL store warning: {e}")

                # 5. Print status (so you know it's not frozen)
                print(f"Row {i+1}/{ROWS_TO_COLLECT}: {row}")
                
                # 6. Wait before next check
                time.sleep(INTERVAL_SEC)

            except Exception as e:
                print(f"Error on row {i}: {e}")
                continue

    print(f"\n--- COLLECTION COMPLETE ---")
    print(f"Data saved to {FILE_NAME}")

if __name__ == "__main__":
    collect_training_data()