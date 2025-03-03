import logging
from typing import List, Dict, Any, Optional
import time
from datetime import datetime, timedelta

from database import Database
from twitter_api import TwitterAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterFollowingTracker:
    """Class to track Twitter users' following lists."""
    
    def __init__(self, api_key: str, db: Database):
        """Initialize the Twitter following tracker.
        
        Args:
            api_key (str): API key for apidance.pro
            db (Database): Database instance
        """
        self.twitter_api = TwitterAPI(api_key)
        self.db = db
    
    def add_user_to_track(self, screen_name: str) -> Optional[int]:
        """Add a new Twitter user to track.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            Optional[int]: ID of the tracked user in the database, or None if failed
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        # Get user info from Twitter API
        user_info = self.twitter_api.get_user_info(screen_name)
        
        if 'error' in user_info:
            logger.error(f"Failed to add user {screen_name}: {user_info['error']}")
            return None
        
        if 'id' not in user_info:
            logger.error(f"Failed to add user {screen_name}: Invalid user info response")
            return None
        
        # Add user to database
        user_id = self.db.add_tracked_user(
            str(user_info['id']),
            user_info['screen_name'],
            user_info['name']
        )
        
        logger.info(f"Added user {screen_name} to tracking list with ID {user_id}")
        return user_id
    
    def update_user_following(self, user_id: int, screen_name: str) -> List[Dict[str, Any]]:
        """Update the following list for a tracked user.
        
        Args:
            user_id (int): ID of the tracked user in the database
            screen_name (str): Twitter screen name
            
        Returns:
            List[Dict[str, Any]]: List of newly added followings
        """
        # Get following list from Twitter API
        following_data = self.twitter_api.get_user_following(screen_name)
        
        if 'error' in following_data:
            logger.error(f"Failed to update following for {screen_name}: {following_data['error']}")
            return []
        
        if 'users' not in following_data:
            logger.error(f"Failed to update following for {screen_name}: Invalid response format")
            return []
        
        # Update database with new following list
        new_followings = self.db.update_following(user_id, following_data['users'])
        
        logger.info(f"Updated following list for {screen_name}, found {len(new_followings)} new followings")
        return new_followings
    
    def update_all_tracked_users(self) -> Dict[str, List[Dict[str, Any]]]:
        """Update following lists for all tracked users.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary mapping screen names to lists of new followings
        """
        tracked_users = self.db.get_tracked_users()
        results = {}
        
        for user in tracked_users:
            logger.info(f"Updating following list for {user['screen_name']}")
            new_followings = self.update_user_following(user['id'], user['screen_name'])
            results[user['screen_name']] = new_followings
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
        
        return results
    
    def initialize_default_users(self) -> None:
        """Initialize the tracker with default users to track."""
        default_users = ["cz_binance", "hosseeb.p"]
        
        for user in default_users:
            logger.info(f"Adding default user {user} to tracking list")
            self.add_user_to_track(user)
