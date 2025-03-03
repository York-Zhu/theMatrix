# Twitter Following Tracker

A tool that tracks Twitter users' following lists and highlights newly added followings through Slack notifications.

## Features

- Tracks Twitter users' following lists every 24 hours
- Detects and highlights newly added followings
- Sends notifications through Slack
- Upgradeable list of tracked users through API endpoints
- RESTful API for managing tracked users and viewing new followings

## Setup

### Prerequisites

- Python 3.8+
- FastAPI
- SQLite (in-memory database for this proof of concept)
- Twitter API access (via apidance.pro)
- Slack webhook URL (for notifications)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/twitter-following-tracker.git
cd twitter-following-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
TWITTER_API_KEY=your_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

### Running the Application

```bash
cd app
uvicorn main:app --reload
```

The application will be available at http://localhost:8000

## API Endpoints

- `GET /users` - List all tracked users
- `POST /users` - Add a new user to track
- `DELETE /users/{screen_name}` - Remove a user from tracking
- `GET /new-followings` - View all new followings that haven't been notified yet
- `POST /update` - Manually trigger an update of all tracked users' following lists
- `GET /test-update/{screen_name}` - Test updating a specific user's following list

## Architecture

- `app/main.py` - FastAPI application entry point
- `database.py` - SQLite database interface
- `twitter_api.py` - Twitter API client
- `tracker.py` - Twitter following tracker
- `user_manager.py` - User management system
- `slack_notifier.py` - Slack notification system
- `scheduler.py` - Scheduled task manager

## Limitations

- Uses an in-memory database, so data will be lost if the application restarts
- Twitter API has rate limits, so tracking a large number of users might require implementing more sophisticated rate limiting

## License

MIT
