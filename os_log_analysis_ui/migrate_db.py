#!/usr/bin/env python3
"""Database migration script to add missing password column"""

import mysql.connector
import sys

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='NewPassword123',
        database='oslog_analysis'
    )
    
    cursor = conn.cursor()
    
    # Check if password column exists
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME='users' AND COLUMN_NAME='password'
    """)
    
    password_col_exists = cursor.fetchone() is not None
    
    if not password_col_exists:
        print("Adding password column to users table...")
        cursor.execute('ALTER TABLE users ADD COLUMN password VARCHAR(255) AFTER username')
        conn.commit()
        print("✓ Password column added successfully")
    else:
        print("✓ Password column already exists")
    
    # Verify the change
    cursor.execute('DESCRIBE users')
    columns = cursor.fetchall()
    print("\nUsers table schema:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
