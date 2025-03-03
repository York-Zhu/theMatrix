import logging
import json
import http.client
import urllib.parse
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SlackNotifier:
    """Class to send notifications to Slack."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize the Slack notifier.
        
        Args:
            webhook_url (Optional[str]): Slack webhook URL. If None, will try to get from environment.
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        
        if not self.webhook_url:
            logger.warning("No Slack webhook URL provided. Notifications will be logged but not sent.")
    
    def _parse_webhook_url(self) -> tuple:
        """Parse the webhook URL into components.
        
        Returns:
            tuple: (host, path) tuple
        """
        if not self.webhook_url:
            return None, None
            
        # Parse the webhook URL
        parsed_url = urllib.parse.urlparse(self.webhook_url)
        host = parsed_url.netloc
        path = parsed_url.path
        
        return host, path
    
    def send_message(self, message: str, blocks: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Send a message to Slack.
        
        Args:
            message (str): Message text
            blocks (Optional[List[Dict[str, Any]]]): Slack blocks for rich formatting
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.info(f"Would send to Slack: {message}")
            return False
            
        host, path = self._parse_webhook_url()
        
        if not host or not path:
            logger.error("Invalid webhook URL format")
            return False
            
        # Prepare the payload
        payload = {
            "text": message
        }
        
        if blocks:
            payload["blocks"] = blocks
            
        payload_json = json.dumps(payload)
        
        # Send the request
        conn = http.client.HTTPSConnection(host)
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            conn.request("POST", path, payload_json, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                logger.error(f"Failed to send Slack notification: {response.status} {response.reason}")
                return False
                
            logger.info(f"Slack notification sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
        finally:
            conn.close()
    
    def notify_new_followings(self, new_followings: List[Dict[str, Any]]) -> bool:
        """Send a notification about new Twitter followings.
        
        Args:
            new_followings (List[Dict[str, Any]]): List of new followings with tracked user info
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not new_followings:
            logger.info("No new followings to notify about")
            return True
            
        # Group followings by tracked user
        followings_by_user = {}
        for following in new_followings:
            tracked_user = following['tracked_screen_name']
            if tracked_user not in followings_by_user:
                followings_by_user[tracked_user] = []
            followings_by_user[tracked_user].append(following)
        
        # Create blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 New Twitter Followings Detected",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(new_followings)}* new followings detected across *{len(followings_by_user)}* tracked users."
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add sections for each tracked user
        for tracked_user, followings in followings_by_user.items():
            # Add tracked user section
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*@{tracked_user}* started following *{len(followings)}* new accounts:"
                }
            })
            
            # Add followings as a list
            following_text = ""
            for following in followings:
                following_text += f"• <https://twitter.com/{following['following_screen_name']}|@{following['following_screen_name']}> - {following['following_name']}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": following_text
                }
            })
            
            blocks.append({
                "type": "divider"
            })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            ]
        })
        
        # Create a simple text summary for clients that don't support blocks
        summary_text = f"🔔 {len(new_followings)} new Twitter followings detected across {len(followings_by_user)} tracked users."
        
        # Send the notification
        return self.send_message(summary_text, blocks)
