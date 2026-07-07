import json
from pathlib import Path
from typing import List, Dict, Any
from database.db import fetch_one
from utils.logger import get_logger

logger = get_logger("itinerary_generator")

ROOT_DIR = Path(__file__).resolve().parent.parent

def generate_itinerary(destination_name: str, days: int) -> List[Dict[str, Any]]:
    """
    Generate a dynamic day-by-day itinerary adapting to the number of days entered.
    Day 1: Arrival, Check-in, Local sightseeing.
    Day 2 -> N-1: Major attractions, activities.
    Day N: Departure, shopping, return.
    """
    try:
        # Fetch destination attractions
        dest = fetch_one("SELECT attractions, description FROM destinations WHERE name = ?", (destination_name,))
        if not dest:
            logger.warning(f"Destination '{destination_name}' not found for itinerary generation.")
            return []
            
        try:
            attractions = json.loads(dest["attractions"])
        except Exception:
            attractions = []
            
        description = dest["description"]
        itinerary = []
        
        # Helper to get attraction safely
        attr_idx = 0
        def get_next_attraction() -> str:
            nonlocal attr_idx
            if not attractions:
                return "Local market walk and leisure time"
            item = attractions[attr_idx % len(attractions)]
            attr_idx += 1
            return item

        for day in range(1, days + 1):
            day_plan = {
                "day": day,
                "morning": "",
                "afternoon": "",
                "evening": "",
                "notes": ""
            }
            
            if day == 1:
                # Arrival Day
                day_plan["morning"] = "Arrival in destination, transfer and check-in to your hotel. Rest and freshen up."
                day_plan["afternoon"] = f"Visit {get_next_attraction()} for a relaxed local introduction."
                day_plan["evening"] = "Take a stroll in the nearby streets, try local street food, and enjoy a quiet dinner."
                day_plan["notes"] = "Keep luggage tags safe; check hotel amenities upon arrival."
                
            elif day == days:
                # Departure Day
                day_plan["morning"] = f"Early visit to {get_next_attraction()} or souvenir shopping in local markets."
                day_plan["afternoon"] = "Enjoy a traditional lunch, return to the hotel for check-out procedures, and head to the transit terminal."
                day_plan["evening"] = "Board your train/bus/flight for the return journey home."
                day_plan["notes"] = "Double-check room lockers and pack all belongings before checking out."
                
            else:
                # Middle Days: Sightseeing
                day_plan["morning"] = f"Guided sightseeing at the famous {get_next_attraction()}. Best visited in the morning."
                day_plan["afternoon"] = f"Explore {get_next_attraction()} followed by a hearty lunch highlighting regional specialties."
                day_plan["evening"] = f"Experience {get_next_attraction()} or enjoy a scenic sunset walk at a nearby vantage point."
                day_plan["notes"] = "Wear comfortable walking shoes and carry a water bottle."
                
            itinerary.append(day_plan)
            
        return itinerary
        
    except Exception as exc:
        logger.error(f"Error generating itinerary: {exc}")
        return []
