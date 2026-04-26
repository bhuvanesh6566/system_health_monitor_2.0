import time
import os
import multiprocessing

def heavy_calculation(x):
    # An infinite loop of heavy math to burn CPU cycles
    while True:
        _ = x * x

def start_cpu_stress():
    print("--- ⚠️ WARNING: STARTING CPU STRESS TEST ⚠️ ---")
    print(f"This will max out your CPU to simulate a system freeze.")
    print("Press 'CTRL + C' to stop immediately.\n")
    
    # Get number of CPU cores to stress all of them
    num_cores = multiprocessing.cpu_count()
    print(f"Launching attack on {num_cores} cores...")
    
    processes = []
    try:
        for i in range(num_cores):
            p = multiprocessing.Process(target=heavy_calculation, args=(i,))
            p.start()
            processes.append(p)
            
        # Keep the main script alive while processes run
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Stress Test... (Cleaning up)")
        for p in processes:
            p.terminate()
        print("✅ CPU Stress Stopped.")

if __name__ == "__main__":
    start_cpu_stress()