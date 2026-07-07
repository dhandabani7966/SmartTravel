from typing import Any, Dict, List, Optional
from database.db import execute, fetch_one, fetch_all, log_audit
from utils.logger import get_logger, log_exception

logger = get_logger("planner")

def save_trip(
    user_id: int,
    destination: str,
    days: int,
    budget: float,
    travelers: int,
    travel_type: str,
    transport_mode: str,
    hotel_category: str,
    estimated_cost: float,
    budget_status: str
) -> int:
    """Save planned trip details into the trips table."""
    try:
        trip_id = execute(
            """
            INSERT INTO trips (
                user_id, destination, days, budget, travelers, travel_type, 
                transport_mode, hotel_category, estimated_cost, budget_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, destination, days, budget, travelers, travel_type,
                transport_mode, hotel_category, estimated_cost, budget_status
            )
        )
        log_audit(user_id, "save_trip", f"Saved trip ID {trip_id} to {destination} ({days} days, budget: ₹{budget}).")
        logger.info(f"Trip ID {trip_id} saved for user {user_id}.")
        return trip_id
    except Exception as exc:
        log_exception(logger, "Failed to save trip", exc)
        raise exc

def delete_trip(trip_id: int, user_id: int, is_admin: bool = False) -> bool:
    """Delete a trip from the database. Admins can delete any trip."""
    try:
        # Check ownership
        trip = fetch_one("SELECT user_id, destination FROM trips WHERE id = ?", (trip_id,))
        if not trip:
            logger.warning(f"Delete failed: Trip ID {trip_id} not found.")
            return False
            
        if not is_admin and trip["user_id"] != user_id:
            logger.warning(f"Delete failed: User {user_id} unauthorized to delete trip ID {trip_id}.")
            return False
            
        execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        log_audit(user_id, "delete_trip", f"Deleted trip ID {trip_id} to {trip['destination']}.")
        logger.info(f"Trip ID {trip_id} deleted by user {user_id}.")
        return True
    except Exception as exc:
        log_exception(logger, f"Failed to delete trip ID {trip_id}", exc)
        return False

def get_user_trips(user_id: int) -> List[Dict[str, Any]]:
    """Get all trips planned by a specific user."""
    try:
        return fetch_all(
            "SELECT id, destination, days, budget, travelers, travel_type, transport_mode, hotel_category, estimated_cost, budget_status, created_at FROM trips WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    except Exception as exc:
        log_exception(logger, f"Failed to fetch trips for user {user_id}", exc)
        return []

def get_all_trips() -> List[Dict[str, Any]]:
    """Get all trips in the system (admin overview)."""
    try:
        return fetch_all(
            """
            SELECT t.id, t.user_id, u.username, t.destination, t.days, t.budget, 
                   t.travelers, t.travel_type, t.transport_mode, t.hotel_category, 
                   t.estimated_cost, t.budget_status, t.created_at 
            FROM trips t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            """
        )
    except Exception as exc:
        log_exception(logger, "Failed to fetch all trips", exc)
        return []

def get_trip_by_id(trip_id: int) -> Optional[Dict[str, Any]]:
    """Fetch details of a specific trip."""
    try:
        return fetch_one(
            "SELECT id, user_id, destination, days, budget, travelers, travel_type, transport_mode, hotel_category, estimated_cost, budget_status, created_at FROM trips WHERE id = ?",
            (trip_id,)
        )
    except Exception as exc:
        log_exception(logger, f"Failed to fetch trip ID {trip_id}", exc)
        return None
