import http.client
import json
import urllib.parse
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterAPI:
    """Class to interact with the Twitter API through apidance.pro."""
    
    def __init__(self, api_key: str):
        """Initialize the Twitter API client.
        
        Args:
            api_key (str): API key for apidance.pro
        """
        self.api_key = api_key
        self.base_url = "api.apidance.pro"
    
    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Make a request to the Twitter API.
        
        Args:
            endpoint (str): API endpoint to call
            params (Dict[str, str]): Query parameters
            
        Returns:
            Dict[str, Any]: Response data as a dictionary
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'apikey': self.api_key
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{endpoint}?{query_string}"
        
        logger.debug(f"Making request to {url}")
        
        try:
            conn.request("GET", url, headers=headers)
            response = conn.getresponse()
            data = response.read()
            
            if response.status != 200:
                logger.error(f"API request failed: {response.status} {response.reason}")
                logger.error(f"Response: {data.decode('utf-8')}")
                return {"error": f"API request failed: {response.status} {response.reason}"}
            
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error making API request: {str(e)}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_user_info(self, screen_name: str) -> Dict[str, Any]:
        """Get information about a Twitter user.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            Dict[str, Any]: User information
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        params = {
            'screen_name': screen_name
        }
        
        return self._make_request("/1.1/users/show.json", params)
    
    def get_user_following(self, screen_name: str, count: int = 200) -> Dict[str, Any]:
        """Get the list of users that a Twitter user is following.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            count (int): Number of users to retrieve (max 200)
            
        Returns:
            Dict[str, Any]: Following list data
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        params = {
            'screen_name': screen_name,
            'count': str(count)
        }
        
        return self._make_request("/1.1/friends/list.json", params)
    
    def get_all_user_following(self, screen_name: str) -> List[Dict[str, Any]]:
        """Get the complete list of users that a Twitter user is following.
        
        This method handles pagination to get all followings, not just the first 200.
        
        Args:
            screen_name (str): Twitter screen name (with or without @)
            
        Returns:
            List[Dict[str, Any]]: Complete list of users being followed
        """
        # Remove @ if present
        screen_name = screen_name.replace('@', '')
        
        all_users = []
        cursor = -1
        
        while cursor != 0:
            params = {
                'screen_name': screen_name,
                'count': '200',
                'cursor': str(cursor)
            }
            
            response = self._make_request("/1.1/friends/list.json", params)
            
            if 'error' in response:
                logger.error(f"Error retrieving following list: {response['error']}")
                break
                
            if 'users' in response:
                all_users.extend(response['users'])
                cursor = response.get('next_cursor', 0)
                logger.info(f"Retrieved {len(response['users'])} followings, next cursor: {cursor}")
            else:
                logger.error(f"Unexpected response format: {response}")
                break
                
            # If we've reached the end or hit an error, stop
            if cursor == 0 or 'error' in response:
                break
        
        logger.info(f"Retrieved a total of {len(all_users)} followings for {screen_name}")
        return all_users
