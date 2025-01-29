
import sqlite3
import json
from threading import Lock
from typing import Dict, Any, List, Optional

class MetadataStore:
    def __init__(self, db_path='metadata.db'):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = Lock()
        self._initialize_db()

    def _initialize_db(self):
        with self.lock:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_metadata (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    method TEXT,
                    url TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON request_metadata (timestamp);
            ''')
            self.connection.commit()

    def add_request_metadata(self, request_data: Dict[str, Any]):
        with self.lock:
            self.cursor.execute('''
                INSERT OR REPLACE INTO request_metadata (id, timestamp, method, url)
                VALUES (?, ?, ?, ?)
            ''', (
                request_data['id'],
                request_data['timestamp'],
                request_data['method'],
                request_data['url']
            ))
            self.connection.commit()

    def search(self, query: Dict[str, str], start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[str]:
        with self.lock:
            conditions = []
            params = []
            # Handle method and URL conditions as before
            for field in ['method', 'url']:
                if field in query:
                    conditions.append(f"{field} LIKE ?")
                    params.append(f"%{query[field]}%")

            # Handle timestamp range
            if start_time:
                conditions.append("timestamp >= ?")
                params.append(start_time)
            if end_time:
                conditions.append("timestamp <= ?")
                params.append(end_time)

            if not conditions:
                return []
            sql_query = f"SELECT id FROM request_metadata WHERE {' AND '.join(conditions)}"
            self.cursor.execute(sql_query, params)
            results = self.cursor.fetchall()
            return [row[0] for row in results]

    def delete_request_metadata(self, request_id: str):
        with self.lock:
            self.cursor.execute('DELETE FROM request_metadata WHERE id = ?', (request_id,))
            self.connection.commit()

    def close(self):
        self.connection.close()
