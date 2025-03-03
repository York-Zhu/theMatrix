import sqlite3
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=":memory:"):
        """Initialize the database connection.
        
        Args:
            db_path (str): Path to the SQLite database file. Default is in-memory database.
        """
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Table to store Twitter users we're tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_users (
            id INTEGER PRIMARY KEY,
            twitter_id TEXT UNIQUE,
            screen_name TEXT UNIQUE,
            name TEXT,
            last_updated TIMESTAMP
        )
        ''')
        
        # Table to store following relationships
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS following (
            id INTEGER PRIMARY KEY,
            tracked_user_id INTEGER,
            following_twitter_id TEXT,
            following_screen_name TEXT,
            following_name TEXT,
            first_seen TIMESTAMP,
            FOREIGN KEY (tracked_user_id) REFERENCES tracked_users (id),
            UNIQUE (tracked_user_id, following_twitter_id)
        )
        ''')
        
        # Table to store newly added followings for notifications
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_followings (
            id INTEGER PRIMARY KEY,
            tracked_user_id INTEGER,
            following_twitter_id TEXT,
            following_screen_name TEXT,
            following_name TEXT,
            detected_at TIMESTAMP,
            notified BOOLEAN DEFAULT 0,
            FOREIGN KEY (tracked_user_id) REFERENCES tracked_users (id),
            UNIQUE (tracked_user_id, following_twitter_id)
        )
        ''')
        
        self.conn.commit()
    
    def add_tracked_user(self, twitter_id, screen_name, name):
        """Add a new user to track.
        
        Args:
            twitter_id (str): Twitter ID of the user.
            screen_name (str): Screen name of the user (without @).
            name (str): Display name of the user.
            
        Returns:
            int: ID of the inserted or existing user.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO tracked_users (twitter_id, screen_name, name, last_updated)
            VALUES (?, ?, ?, NULL)
            ''', (twitter_id, screen_name, name))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # User already exists, get their ID
            cursor.execute('''
            SELECT id FROM tracked_users WHERE twitter_id = ? OR screen_name = ?
            ''', (twitter_id, screen_name))
            return cursor.fetchone()['id']
    
    def get_tracked_users(self):
        """Get all tracked users.
        
        Returns:
            list: List of tracked users as dictionaries.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tracked_users')
        return [dict(row) for row in cursor.fetchall()]
        
    def remove_tracked_user(self, user_id):
        """Remove a tracked user and all their following data.
        
        Args:
            user_id (int): ID of the tracked user.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        cursor = self.conn.cursor()
        try:
            # First delete related records in following and new_followings tables
            cursor.execute('DELETE FROM following WHERE tracked_user_id = ?', (user_id,))
            cursor.execute('DELETE FROM new_followings WHERE tracked_user_id = ?', (user_id,))
            
            # Then delete the user
            cursor.execute('DELETE FROM tracked_users WHERE id = ?', (user_id,))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error removing tracked user: {e}")
            self.conn.rollback()
            return False
    
    def update_following(self, tracked_user_id, following_list):
        """Update the following list for a tracked user.
        
        Args:
            tracked_user_id (int): ID of the tracked user.
            following_list (list): List of users the tracked user is following.
            
        Returns:
            list: List of newly added followings.
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Get current following IDs for this user
        cursor.execute('''
        SELECT following_twitter_id FROM following WHERE tracked_user_id = ?
        ''', (tracked_user_id,))
        current_following_ids = {row['following_twitter_id'] for row in cursor.fetchall()}
        
        # Process new following list
        new_following_ids = set()
        for user in following_list:
            following_id = str(user['id'])
            new_following_ids.add(following_id)
            
            # Insert if not exists
            try:
                cursor.execute('''
                INSERT INTO following 
                (tracked_user_id, following_twitter_id, following_screen_name, following_name, first_seen)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    tracked_user_id, 
                    following_id,
                    user['screen_name'],
                    user['name'],
                    now
                ))
            except sqlite3.IntegrityError:
                # Already exists, skip
                pass
        
        # Find newly added followings (in new list but not in current list)
        newly_added = new_following_ids - current_following_ids
        
        # Add newly detected followings to the new_followings table
        for user in following_list:
            if str(user['id']) in newly_added:
                try:
                    cursor.execute('''
                    INSERT INTO new_followings 
                    (tracked_user_id, following_twitter_id, following_screen_name, following_name, detected_at, notified)
                    VALUES (?, ?, ?, ?, ?, 0)
                    ''', (
                        tracked_user_id, 
                        str(user['id']),
                        user['screen_name'],
                        user['name'],
                        now
                    ))
                except sqlite3.IntegrityError:
                    # Already in new_followings table, skip
                    pass
        
        # Update last_updated timestamp for the tracked user
        cursor.execute('''
        UPDATE tracked_users SET last_updated = ? WHERE id = ?
        ''', (now, tracked_user_id))
        
        self.conn.commit()
        
        # Return newly added followings
        if newly_added:
            cursor.execute('''
            SELECT * FROM following 
            WHERE tracked_user_id = ? AND following_twitter_id IN ({})
            '''.format(','.join(['?'] * len(newly_added))), 
            [tracked_user_id] + list(newly_added))
            return [dict(row) for row in cursor.fetchall()]
        return []
    
    def get_unnotified_new_followings(self):
        """Get all new followings that haven't been notified yet.
        
        Returns:
            list: List of new followings as dictionaries with tracked user info.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT nf.*, tu.screen_name as tracked_screen_name, tu.name as tracked_name
        FROM new_followings nf
        JOIN tracked_users tu ON nf.tracked_user_id = tu.id
        WHERE nf.notified = 0
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_followings_as_notified(self, following_ids):
        """Mark followings as notified.
        
        Args:
            following_ids (list): List of following IDs to mark as notified.
        """
        if not following_ids:
            return
            
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE new_followings SET notified = 1
        WHERE id IN ({})
        '''.format(','.join(['?'] * len(following_ids))), following_ids)
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
