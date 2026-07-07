import json
from pathlib import Path
from typing import Dict, Any, Tuple
from utils.logger import get_logger

logger = get_logger("budget_engine")

ROOT_DIR = Path(__file__).resolve().parent.parent
COST_BASELINE_PATH = ROOT_DIR / "data" / "cost_baseline.json"

def calculate_trip_budget(
    destination_name: str,
    distance_km: int,
    days: int,
    travelers: int,
    travel_type: str,
    transport_mode: str,
    hotel_category: str,
    food_category: str,
    budget_limit: float
) -> Tuple[Dict[str, float], str]:
    """
    Calculate the detailed estimated budget of a trip using Section 6 baselines.
    Returns:
        breakdown: Dict of details (hotel, food, transport, buffer, total).
        status: Budget Status ('Within Budget', 'Near Limit', 'Exceeded').
    """
    try:
        # Load baseline cost JSON
        with open(COST_BASELINE_PATH, "r", encoding="utf-8") as f:
            baseline = json.load(f)
            
        # 1. Transport Calculation
        transport_cost = 0.0
        t_data = baseline["transport"].get(transport_mode)
        
        if not t_data:
            # Fallback default if mode not found
            t_data = baseline["transport"]["TNSTC/private bus"]
            
        t_type = t_data["type"]
        if t_type == "per_km":
            # Round trip distance: distance * 2
            transport_cost = distance_km * 2 * t_data["rate_per_km"] * travelers
        elif t_type == "flat_band":
            if distance_km <= 250:
                rate = t_data["rates"]["short"]
            else:
                rate = t_data["rates"]["long"]
            transport_cost = rate * travelers
        elif t_type == "flat":
            transport_cost = t_data["flat_rate"] * travelers
        elif t_type == "per_day":
            transport_cost = t_data["rate_per_day"] * days
            
        # 2. Hotel Calculation (nights = days - 1, min 1 room for 2 travelers)
        nights = max(0, days - 1)
        rooms = (travelers + 1) // 2
        hotel_rate = baseline["hotels"].get(hotel_category, baseline["hotels"]["Mid-range"])["default"]
        hotel_cost = float(hotel_rate * nights * rooms)
        
        # 3. Food Calculation
        food_rate = baseline["food"].get(food_category, baseline["food"]["Mid-range"])["default"]
        food_cost = float(food_rate * days * travelers)
        
        # 4. Buffer Calculation
        # 15% buffer for Business, 10% for others
        buffer_percent = 0.15 if travel_type.lower() == "business" else 0.10
        subtotal = transport_cost + hotel_cost + food_cost
        buffer_cost = subtotal * buffer_percent
        
        total_cost = subtotal + buffer_cost
        
        breakdown = {
            "transport_cost": round(transport_cost, 2),
            "hotel_cost": round(hotel_cost, 2),
            "food_cost": round(food_cost, 2),
            "buffer_cost": round(buffer_cost, 2),
            "total_cost": round(total_cost, 2)
        }
        
        # 5. Determine Budget Status
        # Within Budget: Total <= 90% of budget
        # Near Limit: Total between 90%-105% of budget
        # Exceeded: Total > 105% of budget
        if total_cost <= (budget_limit * 0.90):
            status = "Within Budget"
        elif total_cost <= (budget_limit * 1.05):
            status = "Near Limit"
        else:
            status = "Exceeded"
            
        return breakdown, status
        
    except Exception as exc:
        logger.error(f"Error calculating trip budget: {exc}")
        return {
            "transport_cost": 0.0,
            "hotel_cost": 0.0,
            "food_cost": 0.0,
            "buffer_cost": 0.0,
            "total_cost": 0.0
        }, "Exceeded"
