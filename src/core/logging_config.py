import logging
import logging.handlers
import os
import sys

LOG_DIR = os.path.join(os.path.expanduser("~"), ".fintechx", "logs")
LOG_FILE = os.path.join(LOG_DIR, "fintechx_app.log")
LOG_LEVEL = logging.INFO # Default level
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(level=LOG_LEVEL):
    """Configures logging for the application."""
    
    # Get the root logger
    logger = logging.getLogger("fintechx_desktop") # Use a specific name for the app logger
    logger.setLevel(level)

    # Prevent adding multiple handlers if called again
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # --- Console Handler --- 
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Rotating File Handler --- 
    # Rotate logs, keeping 5 backups, max 5MB each
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback to console if file logging fails
        logging.getLogger().error(f"Failed to set up file logging: {e}", exc_info=True)

    # Set the root logger level as well if needed, or rely on the specific logger
    # logging.getLogger().setLevel(level)

    logger.info("Logging configured.")

# Example usage (typically called once at application startup)
# if __name__ == "__main__":
#     setup_logging()
#     logging.getLogger("fintechx_desktop.ui").info("UI component started")
#     logging.getLogger("fintechx_desktop.app").warning("Something might be wrong")
#     try:
#         1 / 0
#     except ZeroDivisionError:
#         logging.getLogger("fintechx_desktop.core").error("Critical error", exc_info=True)

