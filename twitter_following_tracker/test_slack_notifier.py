import unittest
from unittest.mock import MagicMock, patch
import json
import http.client
from slack_notifier import SlackNotifier

class TestSlackNotifier(unittest.TestCase):
    def setUp(self):
        self.webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        self.notifier = SlackNotifier(self.webhook_url)
    
    @patch('http.client.HTTPSConnection')
    def test_send_message(self, mock_connection):
        # Set up the mock
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_conn.getresponse.return_value = mock_response
        mock_connection.return_value = mock_conn
        
        # Test sending a simple message
        result = self.notifier.send_message("Test message")
        
        # Verify the connection was made correctly
        mock_connection.assert_called_once_with("hooks.slack.com")
        
        # Verify the request was made correctly
        mock_conn.request.assert_called_once()
        args = mock_conn.request.call_args[0]
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX")
        
        # Verify the payload
        payload = json.loads(args[2])
        self.assertEqual(payload["text"], "Test message")
        
        # Verify the result
        self.assertTrue(result)
    
    @patch('http.client.HTTPSConnection')
    def test_notify_new_followings(self, mock_connection):
        # Set up the mock
        mock_conn = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_conn.getresponse.return_value = mock_response
        mock_connection.return_value = mock_conn
        
        # Test data
        new_followings = [
            {
                "id": 1,
                "tracked_user_id": 1,
                "following_twitter_id": "1001",
                "following_screen_name": "user1",
                "following_name": "User One",
                "detected_at": "2025-03-03T04:00:00",
                "notified": False,
                "tracked_screen_name": "test_user",
                "tracked_name": "Test User"
            },
            {
                "id": 2,
                "tracked_user_id": 1,
                "following_twitter_id": "1002",
                "following_screen_name": "user2",
                "following_name": "User Two",
                "detected_at": "2025-03-03T04:00:00",
                "notified": False,
                "tracked_screen_name": "test_user",
                "tracked_name": "Test User"
            }
        ]
        
        # Test sending a notification
        result = self.notifier.notify_new_followings(new_followings)
        
        # Verify the connection was made correctly
        mock_connection.assert_called_once_with("hooks.slack.com")
        
        # Verify the request was made correctly
        mock_conn.request.assert_called_once()
        
        # Verify the result
        self.assertTrue(result)
    
    def test_no_webhook_url(self):
        # Create a notifier with no webhook URL
        notifier = SlackNotifier(None)
        
        # Test sending a message
        result = notifier.send_message("Test message")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_empty_followings(self):
        # Test with empty followings list
        result = self.notifier.notify_new_followings([])
        
        # Should return True but not make any HTTP requests
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
