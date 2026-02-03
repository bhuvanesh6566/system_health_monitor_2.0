# 🛡️ AI-Powered System Health Monitor

A real-time **AIOps** dashboard that uses Machine Learning (Isolation Forest) to detect system anomalies before they cause a crash. It monitors **OS Metrics**, **Database Performance**, and **Algorithm Efficiency** simultaneously.

## 🚀 Key Features
* **Live Monitoring:** Tracks CPU, RAM, Disk I/O, and Active DB Connections.
* **Algorithm Analysis:** Measures code execution time to detect inefficient logic or infinite loops.
* **Anomaly Detection:** Uses an **Isolation Forest** model to flag abnormal behavior (e.g., CPU spikes or slow queries).
* **Interactive Dashboard:** **React** frontend (Vite + TypeScript) with a control-room style UI; backend exposed via **FastAPI**.

## 🛠️ Tech Stack
* **Backend:** Python 3.10+, FastAPI, same core modules (`os_monitor`, `db_monitor`, `algo_monitor`) + `health_model.pkl`.
* **Frontend:** React 18, TypeScript, Vite, Recharts.
* **Database:** MySQL (Connector).
* **Libraries:** `psutil`, `pandas`, `scikit-learn`, `joblib`, `fastapi`, `uvicorn`.

## ⚙️ Installation & Setup
1.  **Backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Database:**
    * Ensure MySQL is running.
    * Update the `db_config` dictionary in `db_monitor.py` with your username/password.
3.  **Frontend dependencies:**
    ```bash
    cd frontend && npm install
    ```

## 🏃‍♂️ How to Run
**Step 1: Collect Training Data** (run for ~10 mins)
```bash
python collect_data.py
```

**Step 2: Train the model**
```bash
python train_model.py
```

**Step 3: Start the API** (backend) — **run from the project root** (where `api.py` and `requirements.txt` are):
```bash
# From: react mini\
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```
Leave this terminal running.

**Step 4: Start the React frontend** — **in a second terminal**:
```bash
# From: react mini\
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. The frontend proxies `/api` to the backend on port 8000.  
If you see "connect ECONNREFUSED 127.0.0.1:8000", start the API first (Step 3) from the **project root**, not from inside `frontend`.

> **Legacy:** To run the original Streamlit UI: `pip install streamlit plotly` then `streamlit run app.py`
