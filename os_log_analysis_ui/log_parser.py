import pandas as pd
from db_manager import fetch_logs, fetch_logs_raw

def load_logs():
    """Load logs from the database"""
    try:
        logs_data = fetch_logs()
        if logs_data:
            df = pd.DataFrame(logs_data)
            return df.sort_values('timestamp', ascending=False)
        else:
            return pd.DataFrame(columns=['timestamp', 'level', 'source', 'message'])
    except Exception as e:
        print(f"Error loading logs from database: {e}")
        return pd.DataFrame(columns=['timestamp', 'level', 'source', 'message'])
