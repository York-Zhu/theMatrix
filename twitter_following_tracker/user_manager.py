import logging
from typing import List, Dict, Any, Optional
from database import Database
from twitter_api import TwitterAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserManager:
    """Class to manage tracked Twitter users."""
    
    def __init__(self, api_key: str, db: Database):
        """Initialize the user manager.
        
        Args:
            api_key (str): API key for apidance.pro
            db (Database): Database instance
        """
        self.twitter_api = TwitterAPI(api_key)
        self.db = db
    
    def add_user(self, screen_name: str) -> Optional[Dict[str, Any]]:
        """Add a new Twitter user to track.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            Optional[Dict[str, Any]]: User information if successful, None otherwise
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
        
        # Get the user from the database
        users = self.db.get_tracked_users()
        for user in users:
            if user['id'] == user_id:
                return user
        
        return None
    
    def remove_user(self, screen_name: str) -> bool:
        """Remove a Twitter user from tracking.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        # Check if the user exists in the database
        users = self.db.get_tracked_users()
        user_id = None
        
        for user in users:
            if user['screen_name'].lower() == screen_name.lower():
                user_id = user['id']
                break
        
        if user_id is None:
            logger.error(f"Failed to remove user {screen_name}: User not found")
            return False
        
        # Remove the user from the database
        result = self.db.remove_tracked_user(user_id)
        
        if result:
            logger.info(f"Removed user {screen_name} from tracking list")
        else:
            logger.error(f"Failed to remove user {screen_name} from tracking list")
        
        return result
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all tracked users.
        
        Returns:
            List[Dict[str, Any]]: List of tracked users
        """
        return self.db.get_tracked_users()
    
    def get_user(self, screen_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific tracked user.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            Optional[Dict[str, Any]]: User information if found, None otherwise
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        # Check if the user exists in the database
        users = self.db.get_tracked_users()
        
        for user in users:
            if user['screen_name'].lower() == screen_name.lower():
                return user
        
        return None
