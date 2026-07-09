import logging
from utils.path_tool import get_abs_path

import os
from datetime import time, datetime

# Root directory where logs are stored
LOG_ROOT = get_abs_path("logs")

# Make sure the log directory exists
os.makedirs(LOG_ROOT, exist_ok=True)

# Log format config (error / info / debug)
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,      # Only emit INFO and above to console, to avoid noisy DEBUG output
        file_level: int = logging.DEBUG,
        log_file=None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers; if handlers already exist, don't log twice
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    # File handler
    if not log_file:            # Path where the log file is stored
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

# Convenience logger instance
logger = get_logger()

if __name__ == '__main__':
    logger.info("info log")
    logger.error("error log")
    logger.warning("warning log")
    logger.debug("debug log")