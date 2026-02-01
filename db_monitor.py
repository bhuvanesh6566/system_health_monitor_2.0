import mysql.connector

def get_db_metrics():
    """
    Connects to MySQL and returns the number of active threads (connections).
    Returns: int (Active Threads)
    """
    # REPLACE WITH YOUR ACTUAL DATABASE DETAILS
    db_config = {
        'host': 'localhost',
        'user': 'root',          # Change this
        'password': 'bhuvan@10',  # Change this
        'database': 'mysql'      # We connect to the system DB
    }

    try:
        # Establish connection
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Run the status query
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Threads_connected';")
        result = cursor.fetchone() # Returns ('Threads_connected', 'Value')
        
        active_threads = int(result[1])
        
        cursor.close()
        conn.close()
        
        return active_threads

    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return 0  # Return 0 if DB is down

# Test the function if run directly
if __name__ == "__main__":
    print(f"Active DB Connections: {get_db_metrics()}")