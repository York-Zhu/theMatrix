from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime

# Import our modules
import sys
import os
# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database
from twitter_api import TwitterAPI
from tracker import TwitterFollowingTracker
from user_manager import UserManager
from slack_notifier import SlackNotifier
from scheduler import ScheduledTaskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Twitter Following Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# API key for Twitter API
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "socsapueb0mjukcjc2gv1nwwiw3n6m")

# Database instance
db = Database(":memory:")  # Using in-memory database for this proof of concept

# Twitter following tracker
tracker = TwitterFollowingTracker(TWITTER_API_KEY, db)

# User manager
user_manager = UserManager(TWITTER_API_KEY, db)

# Slack notifier
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
slack_notifier = SlackNotifier(slack_webhook_url)

# Scheduled task manager
scheduler = ScheduledTaskManager(TWITTER_API_KEY, db, slack_notifier)

# Initialize default users to track and start scheduler
@app.on_event("startup")
async def startup_event():
    """Initialize the app on startup."""
    logger.info("Initializing Twitter Following Tracker")
    tracker.initialize_default_users()
    logger.info("Initialization complete")
    
    # Start the scheduler to run every 24 hours
    scheduler.start_scheduler(interval_hours=24)
    logger.info("Scheduled task started to run every 24 hours")

# Dependency to get the tracker
def get_tracker():
    return tracker

# Dependency to get the user manager
def get_user_manager():
    return user_manager

# Dependency to get the slack notifier
def get_slack_notifier():
    return slack_notifier
    
# Dependency to get the scheduler
def get_scheduler():
    return scheduler

# Dependency to get the database
def get_db():
    return db

# Models
class TwitterUser(BaseModel):
    screen_name: str

class TrackedUser(BaseModel):
    id: int
    twitter_id: str
    screen_name: str
    name: str
    last_updated: Optional[str] = None

class UserResponse(BaseModel):
    success: bool
    message: str
    user: Optional[TrackedUser] = None

class Following(BaseModel):
    id: int
    tracked_user_id: int
    following_twitter_id: str
    following_screen_name: str
    following_name: str
    first_seen: str

class NewFollowing(BaseModel):
    id: int
    tracked_user_id: int
    following_twitter_id: str
    following_screen_name: str
    following_name: str
    detected_at: str
    notified: bool
    tracked_screen_name: str
    tracked_name: str

# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Twitter Following Tracker API"}

@app.get("/users", response_model=List[TrackedUser])
async def get_tracked_users(db: Database = Depends(get_db)):
    """Get all tracked users."""
    return db.get_tracked_users()

@app.post("/users", response_model=UserResponse)
async def add_tracked_user(
    user: TwitterUser,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Add a new user to track."""
    added_user = user_manager.add_user(user.screen_name)
    
    if added_user is None:
        return UserResponse(
            success=False,
            message=f"Failed to add user {user.screen_name}. User may not exist or API error occurred."
        )
    
    return UserResponse(
        success=True,
        message=f"Successfully added user @{added_user['screen_name']} to tracking list.",
        user=added_user
    )

@app.delete("/users/{screen_name}", response_model=UserResponse)
async def remove_tracked_user(
    screen_name: str,
    user_manager: UserManager = Depends(get_user_manager)
):
    """Remove a user from tracking."""
    # Check if the user exists first
    user = user_manager.get_user(screen_name)
    
    if user is None:
        return UserResponse(
            success=False,
            message=f"User @{screen_name} is not being tracked."
        )
    
    # Remove the user
    result = user_manager.remove_user(screen_name)
    
    if result:
        return UserResponse(
            success=True,
            message=f"Successfully removed user @{screen_name} from tracking list."
        )
    else:
        return UserResponse(
            success=False,
            message=f"Failed to remove user @{screen_name} from tracking list."
        )

@app.post("/update", response_model=Dict[str, List])
async def update_all_users(
    background_tasks: BackgroundTasks,
    tracker: TwitterFollowingTracker = Depends(get_tracker)
):
    """Update following lists for all tracked users."""
    # Run the update in the background
    background_tasks.add_task(tracker.update_all_tracked_users)
    return {"message": "Update started in background"}

@app.get("/new-followings", response_model=List[NewFollowing])
async def get_new_followings(db: Database = Depends(get_db)):
    """Get all new followings that haven't been notified yet."""
    return db.get_unnotified_new_followings()

@app.post("/mark-notified")
async def mark_as_notified(following_ids: List[int], db: Database = Depends(get_db)):
    """Mark followings as notified."""
    db.mark_followings_as_notified(following_ids)
    return {"message": f"Marked {len(following_ids)} followings as notified"}

# For testing purposes
@app.get("/test-update/{screen_name}")
async def test_update_user(
    screen_name: str,
    tracker: TwitterFollowingTracker = Depends(get_tracker),
    db: Database = Depends(get_db)
):
    """Test updating a specific user's following list."""
    # First, make sure the user is being tracked
    user_id = tracker.add_user_to_track(screen_name)
    
    if user_id is None:
        raise HTTPException(status_code=400, detail="Failed to add user")
    
    # Update the user's following list
    new_followings = tracker.update_user_following(user_id, screen_name)
    
    return {
        "user_id": user_id,
        "screen_name": screen_name,
        "new_followings_count": len(new_followings),
        "new_followings": new_followings
    }
