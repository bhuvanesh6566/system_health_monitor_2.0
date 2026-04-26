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

### 📦 MySQL data storage (step-by-step)
Health metrics are stored in MySQL so you can keep history and query later.

1. **Create the monitor database and table**  
   From a terminal (or MySQL Workbench), run:
   ```bash
   mysql -u root -p < schema.sql
   ```
   Or in MySQL client:
   ```sql
   SOURCE path/to/schema.sql;
   ```
   This creates the `aiops_monitor` database and the `health_readings` table.

2. **Set credentials (optional)**  
   By default, `health_storage.py` uses the same host/user/password as `db_monitor` and database name `aiops_monitor`. To override, set:
   ```bash
   set MYSQL_HOST=localhost
   set MYSQL_USER=root
   set MYSQL_PASSWORD=your_password
   set MYSQL_DATABASE=aiops_monitor
   ```
   (Use `export` on Linux/macOS.)

3. **Initialize table from Python (optional)**  
   If you prefer not to run `schema.sql`, you can create the table from code:
   ```bash
   python -c "import health_storage; health_storage.init_db()"
   ```
   (The database `aiops_monitor` must already exist.)

4. **Where data is written**
   * **API:** Each call to `GET /api/health` saves one row to `health_readings`.
   * **Data collection:** Running `python collect_data.py` writes each row to both `system_health.csv` and MySQL.

5. **Read stored data**
   * **API:** `GET /api/history?limit=100` returns recent readings from MySQL (newest first).
   * **Direct:** Use `health_storage.get_recent_readings(limit=50)` in your own scripts.

## 🏃‍♂️ How to Run

### Quick start (Processes & Performance tabs)
The **Processes** tab shows a Task Manager–style list with **app icons** next to each process (when `icoextract` and `Pillow` are installed; see `requirements.txt`).

1. **Start the API** (required first):
   - **Option A:** Double‑click **`start_api.bat`** in the project folder (easiest).
   - **Option B:** In a terminal from the project root:  
     `python -m uvicorn api:app --host 127.0.0.1 --port 8000`
2. **Start the frontend:** Double‑click **`start_frontend.bat`** or run `cd frontend && npm run dev`.
3. Open **http://localhost:5173** in your browser.

If you see **"API error"** or **"Nothing running in server"**, the API is not running — start it with step 1 and keep that window open.

---

**Step 1: Collect Training Data** (for Overview anomaly detection; run for ~10 mins)
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




uvicorn api:app --reload --host 127.0.0.1 --port 8000