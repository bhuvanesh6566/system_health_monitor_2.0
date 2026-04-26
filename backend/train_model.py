import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib  # Used to save the trained model
import os

# --- CONFIGURATION ---
DATA_FILE = "system_health.csv"
MODEL_FILE = "health_model.pkl"

def train_model():
    print("--- 🧠 TRAINING AI MODEL ---")
    
    # 1. Check if data exists
    if not os.path.exists(DATA_FILE):
        print(f"❌ ERROR: '{DATA_FILE}' not found.")
        print("   Run 'collect_data.py' first to generate data.")
        return
    
    # 2. Load the data
    print(f"Loading data from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    
    if len(df) < 50:
        print(f"⚠️ WARNING: You only have {len(df)} rows of data.")
        print("   The model might not be accurate. Recommend collecting >200 rows.")
    
    # 3. Select Features
    # We remove 'Timestamp' because time itself isn't a symptom, 
    # but the CPU/RAM values are.
    features = ['CPU_Percent', 'RAM_Percent', 'Disk_Read_MBs', 'DB_Connections', 'Algo_Time_ms']
    
    try:
        X = df[features]
    except KeyError:
        print("❌ ERROR: CSV columns do not match expected features.")
        print(f"   Expected: {features}")
        print(f"   Found: {list(df.columns)}")
        return

    print(f"Training Isolation Forest on {len(df)} rows...")

    # 4. Train the Model
    # contamination=0.01: We assume 1% of your training data might be random noise.
    # random_state=42: Ensures we get the same result every time we run this.
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)

    # 5. Save the Brain
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Success! Trained model saved to '{MODEL_FILE}'")
    print("   You can now run the dashboard (app.py) or stress tests.")

if __name__ == "__main__":
    train_model()