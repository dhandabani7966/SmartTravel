import json
from pathlib import Path
from typing import Any, Dict, List
from database.db import fetch_all
from utils.logger import get_logger

logger = get_logger("recommendation_engine")

ROOT_DIR = Path(__file__).resolve().parent.parent
COST_BASELINE_PATH = ROOT_DIR / "data" / "cost_baseline.json"

def get_cost_baseline() -> Dict[str, Any]:
    """Load cost baseline constants from JSON."""
    with open(COST_BASELINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend_destinations(
    budget_limit: float,
    days: int,
    travelers: int,
    travel_type: str,
    include_pondicherry: bool = True
) -> List[Dict[str, Any]]:
    """
    Recommend Tamil Nadu destinations based on:
    - User budget (must fit baseline cost minimum)
    - Travel type match (priority rank)
    - Include/Exclude Pondicherry toggle.
    """
    try:
        baseline = get_cost_baseline()
        destinations = fetch_all("SELECT id, name, region, description, attractions, best_season, distance_from_chennai_km FROM destinations")
        
        recommendations = []
        
        # Default estimation parameters:
        # Assuming Mid-range hotel and Mid-range food for recommendations sizing
        hotel_default = baseline["hotels"]["Mid-range"]["default"]
        food_default = baseline["food"]["Mid-range"]["default"]
        # Train flat rate as default transit reference
        transit_default = baseline["transport"]["Train (Sleeper/3AC)"]["rates"]["short"]
        if travelers > 2:
             transit_default = baseline["transport"]["Train (Sleeper/3AC)"]["rates"]["long"]
             
        for dest in destinations:
            name = dest["name"]
            
            # Filter Pondicherry if exclude toggle set
            if name.lower() == "pondicherry" and not include_pondicherry:
                continue
                
            # Parse attractions
            try:
                attractions = json.loads(dest["attractions"])
            except Exception:
                attractions = []
                
            distance = dest["distance_from_chennai_km"]
            
            # Calculate baseline cost to see if it is within budget
            nights = max(1, days - 1)
            
            # Simple transport estimate: if long distance (> 400km), assume long train rates
            if distance > 400:
                transit_cost = baseline["transport"]["Train (Sleeper/3AC)"]["rates"]["long"] * travelers
            else:
                transit_cost = baseline["transport"]["Train (Sleeper/3AC)"]["rates"]["short"] * travelers
                
            # Hotel rooms estimate (1 room per 2 travelers)
            rooms = (travelers + 1) // 2
            hotel_cost = hotel_default * nights * rooms
            food_cost = food_default * days * travelers
            
            # Buffer calculation (default 10% for recommendation screening)
            subtotal = transit_cost + hotel_cost + food_cost
            buffer = subtotal * 0.10
            estimated_cost = subtotal + buffer
            
            # Also calculate minimum possible cost (Budget hotel + Budget food + Bus transport)
            min_hotel = baseline["hotels"]["Budget"]["default"]
            min_food = baseline["food"]["Budget"]["default"]
            min_transit = baseline["transport"]["TNSTC/private bus"]["rate_per_km"] * distance * 2 * travelers
            min_subtotal = min_transit + (min_hotel * nights * rooms) + (min_food * days * travelers)
            min_estimated_cost = min_subtotal + (min_subtotal * 0.10)
            
            # Check if budget is enough for minimum estimated cost
            if budget_limit < min_estimated_cost:
                continue # Skip destination if user budget is too low
                
            # Retrieve trip types (since we didn't store it in DB, let's load it from destinations.json)
            # Wait, the destinations table schema in spec doesn't store trip_types, so let's match with details
            # we can look up destination in the json file directly to find metadata like trip_types.
            dest_json_data = None
            destinations_json_file = ROOT_DIR / "data" / "destinations.json"
            if destinations_json_file.exists():
                with open(destinations_json_file, "r", encoding="utf-8") as f:
                    all_json_dests = json.load(f)
                    for d_json in all_json_dests:
                        if d_json["name"] == name:
                            dest_json_data = d_json
                            break
                            
            trip_types = dest_json_data["trip_types"] if dest_json_data else ["Family", "Solo"]
            
            # Scoring relevance
            score = 0
            # Matches travel type?
            if travel_type in trip_types:
                score += 10
            else:
                score += 2 # Some generic base score
                
            # Best season bonus (if current month is in best season, we could add, but let's keep it simple)
            
            recommendations.append({
                "id": dest["id"],
                "name": name,
                "region": dest["region"],
                "description": dest["description"],
                "attractions": attractions,
                "best_season": dest["best_season"],
                "distance_from_chennai_km": distance,
                "estimated_base_cost": round(estimated_cost, 2),
                "min_possible_cost": round(min_estimated_cost, 2),
                "is_ut": dest_json_data["is_ut"] if dest_json_data else False,
                "match_score": score
            })
            
        # Sort recommendations by match_score descending, then estimated_base_cost ascending
        recommendations.sort(key=lambda x: (-x["match_score"], x["estimated_base_cost"]))
        return recommendations
        
    except Exception as exc:
        logger.error(f"Error in recommend_destinations: {exc}")
        return []
