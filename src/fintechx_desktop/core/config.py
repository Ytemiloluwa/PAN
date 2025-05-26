import configparser
import os
import logging

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".fintechx")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Default configuration values
DEFAULT_CONFIG = {
    "General": {
        "log_level": "INFO",
        "theme": "Light",
    },
    "UI": {
        "window_width": "800",
        "window_height": "600",
    },
    # Add other sections and settings as needed
    # Avoid storing sensitive data like passwords or keys here.
}

def load_config() -> configparser.ConfigParser:
    """Loads the application configuration from the INI file."""
    config = configparser.ConfigParser()
    
    # Set default values first
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in options.items():
            if not config.has_option(section, key):
                config.set(section, key, value)

    # Read the actual config file, overriding defaults if present
    if os.path.exists(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE, encoding="utf-8")
            logging.info(f"Configuration loaded from {CONFIG_FILE}")
        except Exception as e:
            logging.error(f"Failed to read configuration file {CONFIG_FILE}: {e}", exc_info=True)
            # Continue with defaults if reading fails
    else:
        logging.info("Configuration file not found, using defaults.")
        # Save defaults on first run
        save_config(config)
        
    return config

def save_config(config: configparser.ConfigParser):
    """Saves the current configuration to the INI file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as configfile:
            config.write(configfile)
        logging.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logging.error(f"Failed to save configuration file {CONFIG_FILE}: {e}", exc_info=True)

# Load config globally on import (or provide a function to get it)
# Be mindful of when this runs relative to logging setup
# It might be better to have an explicit initialization step
# config = load_config()

# Example usage:
# from .config import load_config, save_config
# config = load_config()
# log_level = config.get("General", "log_level", fallback="INFO")
# config.set("UI", "window_width", "900")
# save_config(config)


