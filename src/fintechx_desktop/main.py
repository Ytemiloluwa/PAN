import sys
import logging
from PyQt6.QtWidgets import QApplication
from .core.logging_config import setup_logging
from .core.config import load_config
from .ui.main_window import MainWindow

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
    main_window = MainWindow()
    main_window.show()

    logger.info("Application UI started.")
    sys.exit(app.exec())


if __name__ == "__main__":
    # This allows running the app directly via `python -m fintechx_desktop.main`
    # Ensure the fintechx_desktop package is in PYTHONPATH or installed.
    run_app()

