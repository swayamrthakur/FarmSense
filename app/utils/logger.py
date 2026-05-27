import sqlite3
import time
from datetime import datetime


DB_PATH = "farmsense.db"


def init_db():
    """Create the logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL,
            disease_risk TEXT,
            response_ms REAL,
            cache_hit INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def log_request(location: str, prediction: str, confidence: float,
                disease_risk: str, response_ms: float, cache_hit: bool):
    """Log every prediction request to SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT INTO api_logs 
               (timestamp, location, prediction, confidence, disease_risk, response_ms, cache_hit)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.utcnow().isoformat(),
                location,
                prediction,
                confidence,
                disease_risk,
                response_ms,
                int(cache_hit)
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")


def get_recent_requests(limit: int = 10) -> list:
    """Fetch recent requests for the dashboard."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            """SELECT timestamp, location, prediction, confidence, 
                      disease_risk, response_ms, cache_hit
               FROM api_logs 
               ORDER BY id DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "location": r[1],
                "prediction": r[2],
                "confidence": r[3],
                "disease_risk": r[4],
                "response_ms": r[5],
                "cache_hit": bool(r[6])
            }
            for r in rows
        ]
    except Exception:
        return []