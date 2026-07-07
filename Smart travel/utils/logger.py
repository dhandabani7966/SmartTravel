import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "application.log"

_CONFIGURED = False

def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.touch(exist_ok=True)

    # Format: TIMESTAMP | LEVEL | MODULE | MESSAGE
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler (2MB limit, keep 3 backup copies)
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(formatter)

    # Root Logger Setup
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Stream Handler for console (optional but helpful for debug)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.getLogger("system").info("Application startup - Logging Initialized")
    _CONFIGURED = True

def get_logger(name: str) -> logging.Logger:
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)

def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    logger.exception("%s | error=%s", message, exc)
