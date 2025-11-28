import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Define constants for log paths
APP_NAME = "MaterialYou-Autothemer"
LOG_DIR = Path.home() / ".cache" / APP_NAME / "logs"
LOG_FILE = LOG_DIR / "backend.log"


def setup_logger(name=APP_NAME):
    """
    Configures and returns a logger instance with console and file handlers.
    """
    # Ensure log directory exists
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Failed to create log directory: {e}", file=sys.stderr)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times if setup_logger is called repeatedly
    if logger.hasHandlers():
        return logger

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    # Max size 5MB, keep 3 backups
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}", file=sys.stderr)

    return logger


# Create a default logger instance for easy import
log = setup_logger()
