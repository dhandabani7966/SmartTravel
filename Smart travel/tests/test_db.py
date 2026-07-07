import unittest
import os
from database.db import init_db, execute, fetch_one, fetch_all, DB_PATH
from auth.auth import register_user, authenticate_user

class TestDatabaseAndAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize database
        init_db()

    def test_database_init(self):
        # Check database file exists
        self.assertTrue(os.path.exists(DB_PATH))
        
        # Check destinations table seeded
        res = fetch_one("SELECT COUNT(*) as count FROM destinations")
        self.assertIsNotNone(res)
        self.assertGreater(res["count"], 0)

    def test_auth_registration_and_login(self):
        # Register a test user
        username = "test_user_unique_123"
        email = "test_user_unique_123@example.com"
        password = "TestPassword@123"
        
        success, msg = register_user(username, email, password)
        self.assertTrue(success, msg)
        
        # Login test
        auth_success, user_data, auth_msg = authenticate_user(username, password)
        self.assertTrue(auth_success, auth_msg)
        self.assertEqual(user_data["username"], username)
        self.assertEqual(user_data["email"], email)
        
        # Clean up test user
        execute("DELETE FROM users WHERE username = ?", (username,))

if __name__ == "__main__":
    unittest.main()
