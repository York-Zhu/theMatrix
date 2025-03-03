import unittest
from unittest.mock import MagicMock, patch
import json

from database import Database
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker

class TestTwitterFollowingTracker(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.api_key = "test_api_key"
        
        # Create a mock TwitterAPI
        self.twitter_api = MagicMock(spec=TwitterAPI)
        
        # Create the tracker with the mock API
        self.tracker = TwitterFollowingTracker(self.api_key, self.db)
        self.tracker.twitter_api = self.twitter_api
    
    def test_add_user_to_track(self):
        # Mock the API response
        self.twitter_api.get_user_info.return_value = {
            "id": 123456,
            "screen_name": "test_user",
            "name": "Test User"
        }
        
        # Add a user to track
        user_id = self.tracker.add_user_to_track("test_user")
        
        # Verify the API was called correctly
        self.twitter_api.get_user_info.assert_called_once_with("test_user")
        
        # Verify the user was added to the database
        users = self.db.get_tracked_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["twitter_id"], "123456")
        self.assertEqual(users[0]["screen_name"], "test_user")
    
    def test_update_user_following(self):
        # Add a user to the database
        user_id = self.db.add_tracked_user("123456", "test_user", "Test User")
        
        # Mock the API response
        self.twitter_api.get_user_following.return_value = {
            "users": [
                {"id": 1001, "screen_name": "follow1", "name": "Follow One"},
                {"id": 1002, "screen_name": "follow2", "name": "Follow Two"}
            ]
        }
        
        # Update the user's following list
        new_followings = self.tracker.update_user_following(user_id, "test_user")
        
        # Verify the API was called correctly
        self.twitter_api.get_user_following.assert_called_once_with("test_user")
        
        # Verify the followings were added to the database
        self.assertEqual(len(new_followings), 2)
        
        # Update again with one new following
        self.twitter_api.get_user_following.return_value = {
            "users": [
                {"id": 1001, "screen_name": "follow1", "name": "Follow One"},
                {"id": 1002, "screen_name": "follow2", "name": "Follow Two"},
                {"id": 1003, "screen_name": "follow3", "name": "Follow Three"}
            ]
        }
        
        new_followings = self.tracker.update_user_following(user_id, "test_user")
        
        # Verify only the new following was returned
        self.assertEqual(len(new_followings), 1)
        self.assertEqual(new_followings[0]["following_twitter_id"], "1003")
    
    def test_initialize_default_users(self):
        # Mock the add_user_to_track method
        self.tracker.add_user_to_track = MagicMock(return_value=1)
        
        # Initialize default users
        self.tracker.initialize_default_users()
        
        # Verify the method was called for each default user
        self.assertEqual(self.tracker.add_user_to_track.call_count, 2)
        self.tracker.add_user_to_track.assert_any_call("cz_binance")
        self.tracker.add_user_to_track.assert_any_call("hosseeb.p")

if __name__ == "__main__":
    unittest.main()
