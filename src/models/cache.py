import sqlite3
import json
from datetime import datetime, timedelta

class Cache:
    def __init__(self, db_path="cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp DATETIME
            )
        """)
        self.conn.commit()

    def get(self, key: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value, timestamp FROM cache WHERE key = ?",
            (key,)
        )
        result = cursor.fetchone()
        
        if result:
            value, timestamp = result
            stored_time = datetime.fromisoformat(timestamp)
            if datetime.now() - stored_time < timedelta(hours=24):
                return json.loads(value)
        return None

    def set(self, key: str, value: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
            (key, json.dumps(value), datetime.now().isoformat())
        )
        self.conn.commit() 