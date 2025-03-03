import unittest
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
    
    def tearDown(self):
        self.db.close()
    
    def test_add_tracked_user(self):
        user_id = self.db.add_tracked_user("123456", "test_user", "Test User")
        self.assertIsNotNone(user_id)
        
        # Test duplicate insertion
        duplicate_id = self.db.add_tracked_user("123456", "test_user", "Test User")
        self.assertEqual(user_id, duplicate_id)
    
    def test_get_tracked_users(self):
        self.db.add_tracked_user("123456", "test_user1", "Test User 1")
        self.db.add_tracked_user("789012", "test_user2", "Test User 2")
        
        users = self.db.get_tracked_users()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['screen_name'], "test_user1")
        self.assertEqual(users[1]['screen_name'], "test_user2")
    
    def test_update_following(self):
        # Add a tracked user
        user_id = self.db.add_tracked_user("123456", "test_user", "Test User")
        
        # Initial following list
        initial_following = [
            {"id": 1001, "screen_name": "follow1", "name": "Follow One"},
            {"id": 1002, "screen_name": "follow2", "name": "Follow Two"}
        ]
        
        new_followings = self.db.update_following(user_id, initial_following)
        self.assertEqual(len(new_followings), 2)  # Both are new
        
        # Update with one new following
        updated_following = [
            {"id": 1001, "screen_name": "follow1", "name": "Follow One"},
            {"id": 1002, "screen_name": "follow2", "name": "Follow Two"},
            {"id": 1003, "screen_name": "follow3", "name": "Follow Three"}
        ]
        
        new_followings = self.db.update_following(user_id, updated_following)
        self.assertEqual(len(new_followings), 1)  # Only one new
        self.assertEqual(new_followings[0]['following_twitter_id'], "1003")
    
    def test_get_unnotified_new_followings(self):
        # Add a tracked user
        user_id = self.db.add_tracked_user("123456", "test_user", "Test User")
        
        # Add some followings
        following_list = [
            {"id": 1001, "screen_name": "follow1", "name": "Follow One"},
            {"id": 1002, "screen_name": "follow2", "name": "Follow Two"}
        ]
        
        self.db.update_following(user_id, following_list)
        
        # Check unnotified followings
        unnotified = self.db.get_unnotified_new_followings()
        self.assertEqual(len(unnotified), 2)
        
        # Mark as notified
        self.db.mark_followings_as_notified([unnotified[0]['id']])
        
        # Check again
        unnotified = self.db.get_unnotified_new_followings()
        self.assertEqual(len(unnotified), 1)

if __name__ == "__main__":
    unittest.main()
