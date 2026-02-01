import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='pest_detections.db'):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pest_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    image_path TEXT,
                    description TEXT
                )
            ''')
            conn.commit()

    def save_detection(self, pest_name, confidence, image_path, description=""):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO detections (pest_name, confidence, image_path, description)
                    VALUES (?, ?, ?, ?)
                ''', (pest_name, confidence, image_path, description))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error saving detection to DB: {e}")
            return None

    def get_history(self, limit=50, offset=0):
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM detections 
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching history from DB: {e}")
            return []

    def get_stats(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM detections')
                total = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT pest_name, COUNT(*) as count 
                    FROM detections 
                    GROUP BY pest_name 
                    ORDER BY count DESC
                ''')
                counts = cursor.fetchall()
                
                return {
                    'total_detections': total,
                    'pest_distribution': dict(counts)
                }
        except Exception as e:
            print(f"Error fetching stats from DB: {e}")
            return {}
