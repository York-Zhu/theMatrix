#!/usr/bin/env python3
"""
Twitter Alert Tool - Main Entry Point

This is the main entry point for the packaged Twitter Alert Tool application.
It starts the FastAPI server and handles the application lifecycle.
"""

import os
import sys
import logging
import uvicorn
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.expanduser("~"), "twitter_alert_tool.log"))
    ]
)
logger = logging.getLogger("twitter_alert_tool")

def get_application_path():
    """Get the path to the application directory."""
    # Check if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

def main():
    """Main entry point for the application."""
    try:
        # Log startup information
        logger.info("Starting Twitter Alert Tool")
        app_path = get_application_path()
        logger.info(f"Application path: {app_path}")
        
        # Add the application directory to the Python path
        sys.path.insert(0, app_path)
        
        # Import the FastAPI app
        from app.main import app
        
        # Start the FastAPI server
        logger.info("Starting FastAPI server")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        logger.error(f"Error starting Twitter Alert Tool: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
