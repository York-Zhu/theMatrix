"""
Logger module for the crypto quantitative trading strategy.
Provides logging functionality for different components of the system.
"""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with the specified name, log file, and level.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to the log file. Defaults to None.
        level (int, optional): Logging level. Defaults to logging.INFO.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        if not log_file.endswith('.log'):
            log_file = f"{log_file}.log"
        
        file_handler = logging.FileHandler(
            os.path.join("logs", log_file)
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create default loggers
data_collection_logger = setup_logger(
    "data_collection", 
    f"data_collection_{datetime.now().strftime('%Y%m%d')}"
)

data_processing_logger = setup_logger(
    "data_processing", 
    f"data_processing_{datetime.now().strftime('%Y%m%d')}"
)

strategy_logger = setup_logger(
    "strategy", 
    f"strategy_{datetime.now().strftime('%Y%m%d')}"
)

# Main logger for the application
main_logger = setup_logger(
    "main", 
    f"main_{datetime.now().strftime('%Y%m%d')}"
)
