import unittest
from unittest.mock import MagicMock, patch
import json
import time
import threading

from database import Database
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker
from slack_notifier import SlackNotifier
from scheduler import ScheduledTaskManager

class TestScheduledTaskManager(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.api_key = "test_api_key"
        
        # Create mock objects
        self.tracker = MagicMock(spec=TwitterFollowingTracker)
        self.slack_notifier = MagicMock(spec=SlackNotifier)
        
        # Create the scheduler
        self.scheduler = ScheduledTaskManager(self.api_key, self.db, self.slack_notifier)
        
        # Replace the tracker with our mock
        self.scheduler.tracker = self.tracker
    
    def test_update_and_notify_no_new_followings(self):
        # Mock the tracker to return no new followings
        self.tracker.update_all_tracked_users.return_value = {
            "test_user": []
        }
        
        # Create a mock for the database methods
        self.db.get_unnotified_new_followings = MagicMock(return_value=[])
        self.db.mark_followings_as_notified = MagicMock()
        
        # Run the update
        self.scheduler.update_and_notify()
        
        # Verify the tracker was called
        self.tracker.update_all_tracked_users.assert_called_once()
        
        # Verify the database was called
        self.db.get_unnotified_new_followings.assert_called_once()
        
        # Verify the notifier was not called
        self.slack_notifier.notify_new_followings.assert_not_called()
    
    def test_update_and_notify_with_new_followings(self):
        # Mock the tracker to return new followings
        self.tracker.update_all_tracked_users.return_value = {
            "test_user": [
                {"id": 1, "following_twitter_id": "1001", "following_screen_name": "follow1"}
            ]
        }
        
        # Mock the database to return unnotified followings
        unnotified_followings = [
            {
                "id": 1,
                "tracked_user_id": 1,
                "following_twitter_id": "1001",
                "following_screen_name": "follow1",
                "following_name": "Follow One",
                "detected_at": "2025-03-03T04:00:00",
                "notified": False,
                "tracked_screen_name": "test_user",
                "tracked_name": "Test User"
            }
        ]
        self.db.get_unnotified_new_followings = MagicMock(return_value=unnotified_followings)
        self.db.mark_followings_as_notified = MagicMock()
        
        # Mock the notifier to return success
        self.slack_notifier.notify_new_followings.return_value = True
        
        # Run the update
        self.scheduler.update_and_notify()
        
        # Verify the tracker was called
        self.tracker.update_all_tracked_users.assert_called_once()
        
        # Verify the database was called
        self.db.get_unnotified_new_followings.assert_called_once()
        
        # Verify the notifier was called
        self.slack_notifier.notify_new_followings.assert_called_once_with(unnotified_followings)
        
        # Verify the followings were marked as notified
        self.db.mark_followings_as_notified.assert_called_once_with([1])
    
    def test_start_and_stop_scheduler(self):
        # Mock the update_and_notify method
        self.scheduler.update_and_notify = MagicMock()
        
        # Start the scheduler
        self.scheduler.start_scheduler()
        
        # Verify the scheduler is running
        self.assertTrue(self.scheduler.is_running)
        self.assertIsNotNone(self.scheduler.scheduler_thread)
        
        # Verify the update was called immediately
        self.scheduler.update_and_notify.assert_called_once()
        
        # Stop the scheduler
        self.scheduler.stop_scheduler()
        
        # Verify the scheduler is stopped
        self.assertFalse(self.scheduler.is_running)

if __name__ == "__main__":
    unittest.main()
