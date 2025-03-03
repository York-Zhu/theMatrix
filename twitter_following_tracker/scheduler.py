import logging
import time
import schedule
import threading
from typing import List, Dict, Any, Optional
import os

from database import Database
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker
from slack_notifier import SlackNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScheduledTaskManager:
    """Class to manage scheduled tasks for the Twitter following tracker."""
    
    def __init__(self, api_key: str, db: Database, slack_notifier: SlackNotifier):
        """Initialize the scheduled task manager.
        
        Args:
            api_key (str): API key for apidance.pro
            db (Database): Database instance
            slack_notifier (SlackNotifier): Slack notifier instance
        """
        self.tracker = TwitterFollowingTracker(api_key, db)
        self.db = db
        self.slack_notifier = slack_notifier
        self.scheduler_thread = None
        self.is_running = False
    
    def update_and_notify(self):
        """Update all tracked users' following lists and send notifications."""
        logger.info("Running scheduled update of Twitter following lists")
        
        try:
            # Update all tracked users
            new_followings_by_user = self.tracker.update_all_tracked_users()
            
            # Collect all new followings
            all_new_followings = []
            for user, followings in new_followings_by_user.items():
                all_new_followings.extend(followings)
            
            # Get unnotified followings from the database
            unnotified_followings = self.db.get_unnotified_new_followings()
            
            if unnotified_followings:
                logger.info(f"Found {len(unnotified_followings)} unnotified new followings")
                
                # Send notification
                notification_sent = self.slack_notifier.notify_new_followings(unnotified_followings)
                
                if notification_sent:
                    # Mark as notified
                    following_ids = [f['id'] for f in unnotified_followings]
                    self.db.mark_followings_as_notified(following_ids)
                    logger.info(f"Marked {len(following_ids)} followings as notified")
                else:
                    logger.error("Failed to send notification, followings will remain unnotified")
            else:
                logger.info("No new followings to notify about")
                
            logger.info("Scheduled update completed successfully")
        except Exception as e:
            logger.error(f"Error in scheduled update: {str(e)}")
    
    def start_scheduler(self, interval_hours: int = 24):
        """Start the scheduler to run tasks at specified intervals.
        
        Args:
            interval_hours (int): Interval in hours between task runs
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        logger.info(f"Starting scheduler to run every {interval_hours} hours")
        
        # Schedule the task
        schedule.every(interval_hours).hours.do(self.update_and_notify)
        
        # Run the task immediately on startup
        self.update_and_notify()
        
        # Start the scheduler in a separate thread
        def run_scheduler():
            self.is_running = True
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True  # Allow the thread to be terminated when the main program exits
        self.scheduler_thread.start()
        
        logger.info("Scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
            
        logger.info("Stopping scheduler")
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        # Clear all scheduled jobs
        schedule.clear()
        
        logger.info("Scheduler stopped successfully")
