import time
import random
import joblib
import pandas as pd
import os_monitor
import db_monitor

# --- CONFIGURATION ---
MODEL_FILE = "health_model.pkl"

def stress_test_algorithm():
    print("--- 🧪 ALGORITHM STRESS & VALIDATION TEST ---")
    
    # 1. Load the AI Brain
    try:
        model = joblib.load(MODEL_FILE)
        print("✅ AI Model loaded successfully.")
    except FileNotFoundError:
        print(f"❌ Error: '{MODEL_FILE}' not found. Train the model first!")
        return

    # 2. Run the "Normal" Algorithm (for comparison)
    print("\n1️⃣ Running NORMAL Algorithm (Size: 20,000 items)...")
    start_normal = time.time()
    normal_list = sorted([random.randint(0, 10000) for _ in range(20000)])
    time_normal = (time.time() - start_normal) * 1000
    print(f"   Time: {time_normal:.2f} ms")

    # 3. Run the "Stressed" Algorithm (The Attack)
    print("\n2️⃣ Running STRESSED Algorithm (Size: 1,000,000 items)...")
    print("   (This mimics a bad code update or data spike)")
    
    start_stress = time.time()
    # 50x larger list to force a lag
    stress_list = sorted([random.randint(0, 10000) for _ in range(10000000)])
    time_stress = (time.time() - start_stress) * 1000
    print(f"   Time: {time_stress:.2f} ms (Significant Lag!)")

    # 4. Ask the AI: "Is this anomaly?"
    # We grab current OS/DB metrics to make the data point complete
    current_os = os_monitor.get_os_metrics()
    current_db = db_monitor.get_db_metrics()
    
    # Create the data point with the STRESSED algorithm time
    # [CPU, RAM, Disk, DB, ALGO_TIME]
    attack_data_point = [[
        current_os[0],  # CPU (likely normal)
        current_os[1],  # RAM
        current_os[2],  # Disk
        current_db,     # DB
        time_stress     # <--- THE ANOMALY
    ]]
    
    print("\n3️⃣ Feeding data to AI Model...")
    print(f"   Input Data: {attack_data_point}")
    
    prediction = model.predict(attack_data_point)[0]
    
    print("\n--- 🏁 RESULT ---")
    if prediction == -1:
        print("✅ SUCCESS: The AI detected the anomaly! (Output: -1)")
        print("   The system correctly identified the slow algorithm.")
    else:
        print("❌ FAILURE: The AI thinks this is normal. (Output: 1)")
        print("   Try increasing the list size in this script to make it even slower.")

if __name__ == "__main__":
    stress_test_algorithm()