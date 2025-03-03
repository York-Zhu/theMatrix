import unittest
from unittest.mock import MagicMock, patch
import json

from database import Database
from twitter_api import TwitterAPI
from user_manager import UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.api_key = "test_api_key"
        
        # Create a mock TwitterAPI
        self.twitter_api = MagicMock(spec=TwitterAPI)
        
        # Create the user manager with the mock API
        self.user_manager = UserManager(self.api_key, self.db)
        self.user_manager.twitter_api = self.twitter_api
    
    def test_add_user(self):
        # Mock the API response
        self.twitter_api.get_user_info.return_value = {
            "id": 123456,
            "screen_name": "test_user",
            "name": "Test User"
        }
        
        # Add a user
        user = self.user_manager.add_user("test_user")
        
        # Verify the API was called correctly
        self.twitter_api.get_user_info.assert_called_once_with("test_user")
        
        # Verify the user was added to the database
        self.assertIsNotNone(user)
        self.assertEqual(user["twitter_id"], "123456")
        self.assertEqual(user["screen_name"], "test_user")
        
        # Verify the user is in the list of tracked users
        users = self.user_manager.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["screen_name"], "test_user")
    
    def test_add_user_with_at_symbol(self):
        # Mock the API response
        self.twitter_api.get_user_info.return_value = {
            "id": 123456,
            "screen_name": "test_user",
            "name": "Test User"
        }
        
        # Add a user with @ symbol
        user = self.user_manager.add_user("@test_user")
        
        # Verify the API was called correctly (without @ symbol)
        self.twitter_api.get_user_info.assert_called_once_with("test_user")
        
        # Verify the user was added to the database
        self.assertIsNotNone(user)
    
    def test_add_user_api_error(self):
        # Mock the API response with an error
        self.twitter_api.get_user_info.return_value = {
            "error": "User not found"
        }
        
        # Try to add a non-existent user
        user = self.user_manager.add_user("nonexistent_user")
        
        # Verify the API was called correctly
        self.twitter_api.get_user_info.assert_called_once_with("nonexistent_user")
        
        # Verify the user was not added
        self.assertIsNone(user)
        
        # Verify no users are in the database
        users = self.user_manager.get_users()
        self.assertEqual(len(users), 0)
    
    def test_remove_user(self):
        # Add a user to the database
        self.db.add_tracked_user("123456", "test_user", "Test User")
        
        # Verify the user exists
        users = self.user_manager.get_users()
        self.assertEqual(len(users), 1)
        
        # Remove the user
        result = self.user_manager.remove_user("test_user")
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the user was removed
        users = self.user_manager.get_users()
        self.assertEqual(len(users), 0)
    
    def test_remove_nonexistent_user(self):
        # Try to remove a non-existent user
        result = self.user_manager.remove_user("nonexistent_user")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_get_user(self):
        # Add a user to the database
        self.db.add_tracked_user("123456", "test_user", "Test User")
        
        # Get the user
        user = self.user_manager.get_user("test_user")
        
        # Verify the user was found
        self.assertIsNotNone(user)
        self.assertEqual(user["twitter_id"], "123456")
        self.assertEqual(user["screen_name"], "test_user")
    
    def test_get_nonexistent_user(self):
        # Try to get a non-existent user
        user = self.user_manager.get_user("nonexistent_user")
        
        # Verify the user was not found
        self.assertIsNone(user)

if __name__ == "__main__":
    unittest.main()
