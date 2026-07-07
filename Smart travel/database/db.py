import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator
from database.schema import SCHEMA
from utils.logger import get_logger, log_exception

logger = get_logger("database")

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "smart_travel.db"
DESTINATIONS_JSON_PATH = ROOT_DIR / "data" / "destinations.json"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def db_transaction() -> Generator[sqlite3.Cursor, None, None]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as exc:
        conn.rollback()
        log_exception(logger, "Database transaction failed", exc)
        raise exc
    finally:
        conn.close()

def execute(query: str, params: tuple = ()) -> int:
    """Execute a query and return the last inserted row ID."""
    with db_transaction() as cursor:
        cursor.execute(query, params)
        return cursor.lastrowid or 0

def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Fetch a single row as a dictionary."""
    conn = get_connection()
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    except Exception as exc:
        log_exception(logger, f"Database fetch_one failed: query={query}", exc)
        raise exc
    finally:
        conn.close()

def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Fetch all rows as a list of dictionaries."""
    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    except Exception as exc:
        log_exception(logger, f"Database fetch_all failed: query={query}", exc)
        raise exc
    finally:
        conn.close()

def log_audit(user_id: Optional[int], event_type: str, description: str) -> None:
    """Record an entry in the audit log table."""
    try:
        execute(
            "INSERT INTO audit_logs (user_id, event_type, description) VALUES (?, ?, ?)",
            (user_id, event_type, description)
        )
    except Exception as exc:
        logger.error(f"Failed to write audit log: {event_type} | {description} | error={exc}")

def init_db() -> None:
    """Initialize database tables and seed destinations if empty."""
    try:
        logger.info("Initializing database...")
        # Create tables
        with db_transaction() as cursor:
            cursor.executescript(SCHEMA)
        
        # Check if destinations already seeded
        dest_count = fetch_one("SELECT COUNT(*) as count FROM destinations")
        if dest_count and dest_count["count"] == 0:
            logger.info("Seeding destinations table...")
            if DESTINATIONS_JSON_PATH.exists():
                with open(DESTINATIONS_JSON_PATH, "r", encoding="utf-8") as f:
                    destinations = json.load(f)
                
                with db_transaction() as cursor:
                    for dest in destinations:
                        cursor.execute(
                            """
                            INSERT INTO destinations (name, region, description, attractions, best_season, distance_from_chennai_km)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                dest["name"],
                                dest["region"],
                                dest["description"],
                                json.dumps(dest["attractions"]),
                                dest["best_season"],
                                dest["distance_from_chennai_km"]
                            )
                        )
                logger.info(f"Successfully seeded {len(destinations)} destinations.")
            else:
                logger.warning(f"Seeding file not found at {DESTINATIONS_JSON_PATH}")
        else:
            logger.info("Destinations already seeded.")
            
    except Exception as exc:
        log_exception(logger, "Database initialization failed", exc)
        raise exc
