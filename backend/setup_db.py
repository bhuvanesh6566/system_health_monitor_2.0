#!/usr/bin/env python3
"""
Setup script to initialize MySQL database for the AI System Monitor.
Run this ONCE to:
1. Create the database
2. Create tables
3. Verify connection
"""

import os
import sys
import logging
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_admin_connection():
    """Connect to MySQL as admin (no database selected)."""
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "")
    )

def setup_database():
    """Create database and tables."""
    conn = None
    try:
        # Step 1: Connect as admin
        logger.info("Connecting to MySQL server...")
        conn = get_admin_connection()
        cursor = conn.cursor()
        
        db_name = os.environ.get("MYSQL_DATABASE", "aiops_monitor")
        
        # Step 2: Create database
        logger.info(f"Creating database '{db_name}' if not exists...")
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {db_name}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
        """)
        conn.commit()
        logger.info(f"✓ Database '{db_name}' ready")
        
        # Step 3: Switch to the database
        cursor.execute(f"USE {db_name}")
        
        # Step 4: Create health_readings table
        logger.info("Creating 'health_readings' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_readings (
                id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                recorded_at    DATETIME(3)     NOT NULL,
                cpu_percent    DECIMAL(6,2)   NOT NULL,
                ram_percent    DECIMAL(6,2)   NOT NULL,
                disk_read_mbs  DECIMAL(10,4)  NOT NULL,
                db_connections INT UNSIGNED   NOT NULL,
                algo_time_ms   DECIMAL(10,4)  NOT NULL,
                is_healthy     TINYINT(1)     NULL COMMENT '1=healthy, 0=anomaly, NULL=unknown',
                created_at     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_recorded_at (recorded_at),
                INDEX idx_healthy (is_healthy)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
        logger.info("✓ Table 'health_readings' created")
        
        # Step 5: Verify table
        cursor.execute("DESCRIBE health_readings")
        columns = cursor.fetchall()
        logger.info(f"✓ Table has {len(columns)} columns")
        
        cursor.close()
        logger.info("\n✓✓✓ Database setup COMPLETE! ✓✓✓")
        return True
        
    except Error as e:
        logger.error(f"✗ MySQL Error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   AI System Monitor - MySQL Database Setup")
    print("="*60 + "\n")
    
    success = setup_database()
    sys.exit(0 if success else 1)
