import mysql.connector
import pandas as pd

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",          # your mysql username
    password="NewPassword123",      # your mysql password
    database="oslog_analysis"
)

cursor = conn.cursor()

def insert_logs(df):
    """Insert logs from dataframe into database"""
    try:
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO logs (system_id, level_id, log_time, source, message, event_type) VALUES (%s, %s, %s, %s, %s, %s)",
                (1, 1, pd.Timestamp.now(), row.get('source', 'System'), row.get('message', ''), 'GENERAL')
            )
        conn.commit()
    except Exception as e:
        print(f"Error inserting logs: {e}")

def fetch_logs():
    """Fetch logs from database with level names"""
    try:
        query = """
        SELECT 
            l.log_id as id,
            l.log_time as timestamp,
            ll.level_name as level,
            l.source,
            l.message,
            l.event_type,
            ll.color_code
        FROM logs l
        JOIN log_levels ll ON l.level_id = ll.level_id
        ORDER BY l.log_time DESC
        LIMIT 100
        """
        cursor.execute(query)
        columns = ['id', 'timestamp', 'level', 'source', 'message', 'event_type', 'color_code']
        results = cursor.fetchall()
        return [dict(zip(columns, row)) for row in results] if results else []
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def fetch_logs_raw():
    """Fetch raw log tuples"""
    try:
        query = """
        SELECT 
            l.log_id,
            l.log_time,
            ll.level_name,
            l.source,
            l.message
        FROM logs l
        JOIN log_levels ll ON l.level_id = ll.level_id
        ORDER BY l.log_time DESC
        LIMIT 100
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def get_log_statistics():
    """Get statistics about logs"""
    try:
        query = """
        SELECT 
            ll.level_name,
            COUNT(*) as count,
            ll.color_code
        FROM logs l
        JOIN log_levels ll ON l.level_id = ll.level_id
        GROUP BY ll.level_name, ll.color_code
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return []
