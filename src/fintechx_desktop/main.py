import sys
import logging
from PySide6.QtWidgets import QApplication
import os

from .core.logging_config import setup_logging, LOG_LEVEL
from .core.config import load_config
from .ui.main_window import MainWindow
# Import auth functions if needed for initial setup/login logic integration
# from .app.auth import create_user, authenticate_user 

def run_app():
    # 1. Load Configuration
    config = load_config()
    log_level_str = config.get("General", "log_level", fallback="INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # 2. Setup Logging
    setup_logging(level=log_level)
    logger = logging.getLogger("fintechx_desktop.main")
    logger.info("Starting FinTechX Desktop Application...")
    logger.info(f"Log level set to: {log_level_str}")

    # 3. Initialize Application UI
    app = QApplication(sys.argv)
    main_window = MainWindow() # MainWindow now handles its own setup
    main_window.show()

    # --- Initial Setup/Login Logic (Example - needs refinement) ---
    # This part needs proper integration with the UI login screen signals
    # For now, the MainWindow starts at the login screen placeholder.
    # A real implementation would:
    # - Show login screen.
    # - On successful login (using authenticate_user), call main_window.show_dashboard().
    # - Potentially handle initial user creation if DB is empty.
    # Example check (needs db_password management):
    # db_pass = "user_provided_or_derived_password" # How to get this securely?
    # if not authenticate_user(db_pass, "testuser", "password123"):
    #     logger.error("Initial auth check failed - showing login.")
    #     main_window.show_login_screen()
    # else:
    #     logger.info("User authenticated - showing dashboard.")
    #     main_window.show_dashboard()

    logger.info("Application UI started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    # This allows running the app directly via `python -m fintechx_desktop.main`
    # Ensure the fintechx_desktop package is in PYTHONPATH or installed.
    run_app()

