import logging
import time
import threading
from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch

from database import Database
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker
from slack_notifier import SlackNotifier
from scheduler import ScheduledTaskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestScheduledTask:
    """Test the scheduled task functionality."""
    
    def __init__(self):
        """Initialize the test."""
        self.api_key = "socsapueb0mjukcjc2gv1nwwiw3n6m"
        self.db = Database(":memory:")
        self.slack_notifier = SlackNotifier(None)  # No webhook URL, will log instead of sending
        self.tracker = TwitterFollowingTracker(self.api_key, self.db)
        self.scheduler = ScheduledTaskManager(self.api_key, self.db, self.slack_notifier)
    
    def setup_test_data(self):
        """Set up test data for the scheduled task test."""
        logger.info("Setting up test data...")
        
        # Add test users to track
        user1_id = self.tracker.add_user_to_track("cz_binance")
        
        if not user1_id:
            logger.error("Failed to add test user")
            return False
        
        logger.info(f"Added test user with ID {user1_id}")
        
        # Update the following list (first time, no new followings yet)
        logger.info("Updating following list (first time)...")
        self.tracker.update_user_following(user1_id, "cz_binance")
        
        return True
    
    def test_scheduled_execution(self):
        """Test that the scheduled task executes at the specified interval."""
        logger.info("Testing scheduled execution...")
        
        # Set up a very short interval for testing (10 seconds)
        test_interval_seconds = 10
        
        # Mock the update_and_notify method to track calls
        original_method = self.scheduler.update_and_notify
        call_count = [0]  # Use a list to allow modification in the inner function
        
        def mock_update_and_notify():
            call_count[0] += 1
            logger.info(f"Mock update_and_notify called (count: {call_count[0]})")
            return original_method()
        
        self.scheduler.update_and_notify = mock_update_and_notify
        
        # Start the scheduler with a short interval
        logger.info(f"Starting scheduler with {test_interval_seconds} second interval...")
        
        # Use hours=1/360 to convert 10 seconds to hours (since the scheduler uses hours)
        self.scheduler.start_scheduler(interval_hours=test_interval_seconds/3600)
        
        # Wait for a bit more than two intervals to ensure it runs at least twice
        wait_time = test_interval_seconds * 2.5
        logger.info(f"Waiting for {wait_time} seconds to verify multiple executions...")
        time.sleep(wait_time)
        
        # Stop the scheduler
        self.scheduler.stop_scheduler()
        
        # Check that it was called at least twice (once immediately and once after the interval)
        if call_count[0] >= 2:
            logger.info(f"Scheduler executed {call_count[0]} times as expected")
            return True
        else:
            logger.error(f"Scheduler only executed {call_count[0]} times, expected at least 2")
            return False
    
    def test_following_detection(self):
        """Test that the scheduled task correctly detects new followings."""
        logger.info("Testing following detection...")
        
        # Set up test data
        if not self.setup_test_data():
            return False
        
        # Get the tracked user
        users = self.db.get_tracked_users()
        if not users:
            logger.error("No tracked users found")
            return False
        
        user_id = users[0]['id']
        
        # Simulate a new following by directly adding to the database
        logger.info("Simulating new following...")
        cursor = self.db.conn.cursor()
        now = datetime.now().isoformat()
        
        # Add a new following
        cursor.execute('''
        INSERT INTO following 
        (tracked_user_id, following_twitter_id, following_screen_name, following_name, first_seen)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, "12345", "new_crypto_project", "New Crypto Project", now))
        
        # Add to new_followings table
        cursor.execute('''
        INSERT INTO new_followings 
        (tracked_user_id, following_twitter_id, following_screen_name, following_name, detected_at, notified)
        VALUES (?, ?, ?, ?, ?, 0)
        ''', (user_id, "12345", "new_crypto_project", "New Crypto Project", now))
        
        self.db.conn.commit()
        
        # Mock the tracker's update_all_tracked_users method to return our simulated data
        self.tracker.update_all_tracked_users = MagicMock(return_value={
            users[0]['screen_name']: [
                {
                    "id": 1,
                    "following_twitter_id": "12345",
                    "following_screen_name": "new_crypto_project",
                    "following_name": "New Crypto Project",
                    "first_seen": now
                }
            ]
        })
        
        # Run the update and notify process
        logger.info("Running update and notify process...")
        self.scheduler.update_and_notify()
        
        # Check that the notification was attempted
        unnotified = self.db.get_unnotified_new_followings()
        
        if unnotified:
            logger.info(f"Found {len(unnotified)} unnotified followings as expected")
            return True
        else:
            logger.error("No unnotified followings found")
            return False
    
    def run_all_tests(self):
        """Run all scheduled task tests."""
        logger.info("Starting scheduled task tests...")
        
        # Run the tests
        execution_test = self.test_scheduled_execution()
        detection_test = self.test_following_detection()
        
        # Print summary
        logger.info("Scheduled task tests completed")
        logger.info(f"Scheduled execution test: {'PASSED' if execution_test else 'FAILED'}")
        logger.info(f"Following detection test: {'PASSED' if detection_test else 'FAILED'}")
        
        if execution_test and detection_test:
            logger.info("All scheduled task tests PASSED")
            return True
        else:
            logger.error("Some scheduled task tests FAILED")
            return False

if __name__ == "__main__":
    test = TestScheduledTask()
    test.run_all_tests()
