import logging
import json
from database import Database
from slack_notifier import SlackNotifier
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_slack_notification_format():
    """Test the format of Slack notifications with sample data."""
    # Create a sample notification with test data
    new_followings = [
        {
            "id": 1,
            "tracked_user_id": 1,
            "following_twitter_id": "1001",
            "following_screen_name": "crypto_exchange",
            "following_name": "Crypto Exchange",
            "detected_at": "2025-03-03T04:00:00",
            "notified": False,
            "tracked_screen_name": "cz_binance",
            "tracked_name": "CZ 🔶 BNB"
        },
        {
            "id": 2,
            "tracked_user_id": 1,
            "following_twitter_id": "1002",
            "following_screen_name": "blockchain_dev",
            "following_name": "Blockchain Developer",
            "detected_at": "2025-03-03T04:00:00",
            "notified": False,
            "tracked_screen_name": "cz_binance",
            "tracked_name": "CZ 🔶 BNB"
        },
        {
            "id": 3,
            "tracked_user_id": 2,
            "following_twitter_id": "1003",
            "following_screen_name": "crypto_analyst",
            "following_name": "Crypto Analyst",
            "detected_at": "2025-03-03T04:00:00",
            "notified": False,
            "tracked_screen_name": "hosseeb.p",
            "tracked_name": "Haseeb Qureshi"
        }
    ]
    
    # Create a notifier without a webhook URL (will log instead of sending)
    notifier = SlackNotifier(None)
    
    # Test the notification
    logger.info("Testing Slack notification format...")
    notifier.notify_new_followings(new_followings)
    
    logger.info("Slack notification format test completed")
    return True

def test_slack_integration_with_api_data():
    """Test the Slack integration with real API data."""
    # Initialize components
    api_key = "socsapueb0mjukcjc2gv1nwwiw3n6m"
    db = Database(":memory:")
    twitter_api = TwitterAPI(api_key)
    tracker = TwitterFollowingTracker(api_key, db)
    notifier = SlackNotifier(None)  # No webhook URL, will log instead of sending
    
    # Add the test users to track
    logger.info("Adding test users to track...")
    user1_id = tracker.add_user_to_track("cz_binance")
    user2_id = tracker.add_user_to_track("hosseeb.p")
    
    if not user1_id or not user2_id:
        logger.error("Failed to add test users")
        return False
    
    # Update the following lists (first time, no new followings yet)
    logger.info("Updating following lists (first time)...")
    tracker.update_user_following(user1_id, "cz_binance")
    tracker.update_user_following(user2_id, "hosseeb.p")
    
    # Simulate new followings by directly adding to the database
    logger.info("Simulating new followings...")
    cursor = db.conn.cursor()
    now = "2025-03-03T04:00:00"
    
    # Add a new following for cz_binance
    cursor.execute('''
    INSERT INTO new_followings 
    (tracked_user_id, following_twitter_id, following_screen_name, following_name, detected_at, notified)
    VALUES (?, ?, ?, ?, ?, 0)
    ''', (user1_id, "12345", "new_crypto_project", "New Crypto Project", now))
    
    # Add a new following for hosseeb.p
    cursor.execute('''
    INSERT INTO new_followings 
    (tracked_user_id, following_twitter_id, following_screen_name, following_name, detected_at, notified)
    VALUES (?, ?, ?, ?, ?, 0)
    ''', (user2_id, "67890", "defi_protocol", "DeFi Protocol", now))
    
    db.conn.commit()
    
    # Get unnotified followings
    unnotified_followings = db.get_unnotified_new_followings()
    
    if not unnotified_followings:
        logger.error("No unnotified followings found")
        return False
    
    logger.info(f"Found {len(unnotified_followings)} unnotified followings")
    
    # Test sending notification
    logger.info("Testing Slack notification with simulated data...")
    notifier.notify_new_followings(unnotified_followings)
    
    # Mark as notified
    following_ids = [f['id'] for f in unnotified_followings]
    db.mark_followings_as_notified(following_ids)
    
    # Verify they were marked as notified
    unnotified_followings = db.get_unnotified_new_followings()
    if unnotified_followings:
        logger.error(f"Still have {len(unnotified_followings)} unnotified followings after marking")
        return False
    
    logger.info("Slack integration test with API data completed successfully")
    return True

def test_slack_error_handling():
    """Test error handling for Slack API failures."""
    # Create a notifier with an invalid webhook URL
    notifier = SlackNotifier("https://invalid.webhook.url")
    
    # Create sample data
    new_followings = [
        {
            "id": 1,
            "tracked_user_id": 1,
            "following_twitter_id": "1001",
            "following_screen_name": "crypto_exchange",
            "following_name": "Crypto Exchange",
            "detected_at": "2025-03-03T04:00:00",
            "notified": False,
            "tracked_screen_name": "cz_binance",
            "tracked_name": "CZ 🔶 BNB"
        }
    ]
    
    # Test the notification (should handle the error gracefully)
    logger.info("Testing Slack error handling...")
    result = notifier.notify_new_followings(new_followings)
    
    if result:
        logger.error("Expected notification to fail with invalid webhook URL")
        return False
    
    logger.info("Slack error handling test completed successfully")
    return True

if __name__ == "__main__":
    logger.info("Starting Slack integration tests...")
    
    # Run the tests
    format_test = test_slack_notification_format()
    api_test = test_slack_integration_with_api_data()
    error_test = test_slack_error_handling()
    
    # Print summary
    logger.info("Slack integration tests completed")
    logger.info(f"Format test: {'PASSED' if format_test else 'FAILED'}")
    logger.info(f"API data test: {'PASSED' if api_test else 'FAILED'}")
    logger.info(f"Error handling test: {'PASSED' if error_test else 'FAILED'}")
    
    if format_test and api_test and error_test:
        logger.info("All Slack integration tests PASSED")
    else:
        logger.error("Some Slack integration tests FAILED")
