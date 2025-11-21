"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path
from src.config import settings


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'app.log'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    
    logging.info("Logging configured successfully")


# Initialize logging
setup_logging()

# Get logger for use in other modules
logger = logging.getLogger(__name__)
