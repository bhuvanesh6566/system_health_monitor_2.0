# 🛡️ AI-Powered System Health Monitor

A real-time **AIOps** dashboard that uses Machine Learning (Isolation Forest) to detect system anomalies before they cause a crash. It monitors **OS Metrics**, **Database Performance**, and **Algorithm Efficiency** simultaneously.

## 🚀 Key Features
* **Live Monitoring:** Tracks CPU, RAM, Disk I/O, and Active DB Connections.
* **Algorithm Analysis:** Measures code execution time to detect inefficient logic or infinite loops.
* **Anomaly Detection:** Uses an **Isolation Forest** model to flag abnormal behavior (e.g., CPU spikes or slow queries).
* **Interactive Dashboard:** Built with **Streamlit** for real-time visualization.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **ML Algorithm:** Isolation Forest (Scikit-learn)
* **Frontend:** Streamlit
* **Database:** MySQL (Connector)
* **Libraries:** `psutil`, `pandas`, `plotly`, `joblib`

## ⚙️ Installation & Setup
1.  **Install Dependencies:**
    ```bash
    pip install psutil mysql-connector-python scikit-learn pandas streamlit plotly
    ```
2.  **Configure Database:**
    * Ensure MySQL is running.
    * Update the `db_config` dictionary in `db_monitor.py` with your username/password.

## 🏃‍♂️ How to Run
**Step 1: Collect Training Data** (Run for ~10 mins)
```bash
python collect_data.py

python train_model.py

streamlit run app.py
