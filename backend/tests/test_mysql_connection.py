#!/usr/bin/env python3
"""
Test script to verify MySQL connection and basic functionality.
Run this to ensure everything is configured correctly.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import after loading .env
import mysql.connector
from mysql.connector import Error

def test_connection():
    """Test MySQL connection."""
    logger.info("Testing MySQL connection...")
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "aiops_user"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "aiops_monitor")
        )
        
        if conn.is_connected():
            logger.info("✓ Successfully connected to MySQL")
            
            # Get connection info
            db_info = conn.get_server_info()
            logger.info(f"✓ MySQL Server version: {db_info}")
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            logger.info(f"✓ Current database: {result[0]}")
            
            # Count existing records
            cursor.execute("SELECT COUNT(*) FROM health_readings")
            count = cursor.fetchone()[0]
            logger.info(f"✓ Current records in health_readings: {count}")
            
            cursor.close()
            return True
    except Error as e:
        logger.error(f"✗ Connection failed: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.info("Connection closed")

def test_insert():
    """Test inserting a sample record."""
    logger.info("\nTesting INSERT operation...")
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "aiops_user"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "aiops_monitor")
        )
        
        cursor = conn.cursor()
        
        # Insert test data
        test_data = (
            datetime.now(),
            45.5,      # CPU
            62.3,      # RAM
            125.75,    # Disk Read MBs
            3,         # DB Connections
            5.23,      # Algo Time ms
            1          # is_healthy
        )
        
        cursor.execute("""
            INSERT INTO health_readings
            (recorded_at, cpu_percent, ram_percent, disk_read_mbs, db_connections, algo_time_ms, is_healthy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, test_data)
        
        conn.commit()
        logger.info(f"✓ Successfully inserted test record (ID: {cursor.lastrowid})")
        
        # Verify insert
        cursor.execute("SELECT COUNT(*) FROM health_readings")
        count = cursor.fetchone()[0]
        logger.info(f"✓ Total records now: {count}")
        
        cursor.close()
        return True
    except Error as e:
        logger.error(f"✗ Insert failed: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def test_query():
    """Test querying records."""
    logger.info("\nTesting SELECT query...")
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "aiops_user"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "aiops_monitor")
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, recorded_at, cpu_percent, ram_percent, is_healthy
            FROM health_readings
            ORDER BY id DESC
            LIMIT 5
        """)
        
        records = cursor.fetchall()
        logger.info(f"✓ Retrieved {len(records)} records")
        
        if records:
            logger.info("\nLast 5 records:")
            for row in records:
                logger.info(f"  ID: {row[0]}, Time: {row[1]}, CPU: {row[2]}%, RAM: {row[3]}%, Healthy: {row[4]}")
        
        cursor.close()
        return True
    except Error as e:
        logger.error(f"✗ Query failed: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   MySQL Connection Test Suite")
    print("="*60 + "\n")
    
    results = []
    results.append(("Connection Test", test_connection()))
    results.append(("Insert Test", test_insert()))
    results.append(("Query Test", test_query()))
    
    print("\n" + "="*60)
    print("   Test Results Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)
