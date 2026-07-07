import unittest
from services.recommendation_engine import recommend_destinations
from services.budget_engine import calculate_trip_budget
from services.itinerary_generator import generate_itinerary
from database.db import init_db

class TestTravelPlannerEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_recommendation_engine(self):
        # High budget should recommend everything including Ooty
        recs = recommend_destinations(budget_limit=80000.0, days=5, travelers=2, travel_type="Family")
        self.assertGreater(len(recs), 0)
        
        # Verify region best season structure
        first_rec = recs[0]
        self.assertIn("name", first_rec)
        self.assertIn("region", first_rec)
        self.assertIn("estimated_base_cost", first_rec)

    def test_budget_engine(self):
        # Calculate budget for Chennai
        breakdown, status = calculate_trip_budget(
            destination_name="Ooty",
            distance_km=565,
            days=4,
            travelers=2,
            travel_type="Family",
            transport_mode="Train (Sleeper/3AC)",
            hotel_category="Mid-range",
            food_category="Mid-range",
            budget_limit=15000.0
        )
        self.assertGreater(breakdown["total_cost"], 0.0)
        self.assertIn(status, ["Within Budget", "Near Limit", "Exceeded"])
        
        # Check components
        self.assertGreater(breakdown["hotel_cost"], 0.0)
        self.assertGreater(breakdown["food_cost"], 0.0)
        self.assertGreater(breakdown["transport_cost"], 0.0)

    def test_itinerary_generator(self):
        itinerary = generate_itinerary("Ooty", 3)
        self.assertEqual(len(itinerary), 3)
        
        # Check Day structures
        day1 = itinerary[0]
        self.assertEqual(day1["day"], 1)
        self.assertTrue(len(day1["morning"]) > 0)
        self.assertTrue(len(day1["afternoon"]) > 0)

if __name__ == "__main__":
    unittest.main()
