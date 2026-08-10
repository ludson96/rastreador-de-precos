"""
Database module for storing and querying price scraping history using SQLite.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from src.models.product import PriceResult, ScrapingStatus


class PriceHistoryDB:
    """
    SQLite database helper for persistent price history and health tracking.
    """

    def __init__(self, db_path: str = "data/price_history.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    store_key TEXT NOT NULL,
                    store_name TEXT NOT NULL,
                    store_url TEXT,
                    price REAL,
                    target_price REAL NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_result(self, result: PriceResult) -> None:
        """Saves a single PriceResult into SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_history (
                    product_id, product_name, store_key, store_name, store_url,
                    price, target_price, status, error_message, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.product_id,
                result.product_name,
                result.store_key,
                result.store_name,
                result.store_url,
                result.current_price,
                result.target_price,
                result.status.value if isinstance(result.status, ScrapingStatus) else str(result.status),
                result.error_message,
                result.timestamp.isoformat()
            ))
            conn.commit()

    def save_results(self, results: List[PriceResult]) -> None:
        """Saves multiple PriceResult objects into SQLite."""
        for res in results:
            self.save_result(res)

    def get_lowest_price_24h(self, product_id: str, store_key: str) -> Optional[float]:
        """
        Calculates the lowest recorded price for a product in a specific store in the last 24 hours.
        """
        since_time = (datetime.now() - timedelta(hours=24)).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MIN(price) as min_price
                FROM price_history
                WHERE product_id = ? AND store_key = ? AND price IS NOT NULL AND timestamp >= ?
            """, (product_id, store_key, since_time))
            row = cursor.fetchone()
            if row and row["min_price"] is not None:
                return float(row["min_price"])
        return None
