import mysql.connector
import time

_db_cache = {"value": 1, "timestamp": 0}
CACHE_DURATION = 2  # Cache for 2 seconds

def get_db_metrics():
    """
    Connects to MySQL and returns the number of active threads (connections).
    Returns: int (Active Threads)
    """
    # Use cache to avoid slow DB calls
    now = time.time()
    if now - _db_cache["timestamp"] < CACHE_DURATION:
        return _db_cache["value"]
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'bhuvan@10',
        'database': 'mysql',
        'connection_timeout': 2  # 2 second timeout
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Threads_connected';")
        result = cursor.fetchone()
        active_threads = int(result[1])
        cursor.close()
        conn.close()
        
        _db_cache["value"] = active_threads
        _db_cache["timestamp"] = now
        return active_threads

    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return _db_cache["value"]  # Return cached value on error

# Test the function if run directly
if __name__ == "__main__":
    print(f"Active DB Connections: {get_db_metrics()}")