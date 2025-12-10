import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "output_directory": ".",
    "max_concurrent_chapter_downloads": 3,
    "max_concurrent_image_downloads": 15,
    "window_size": "800x700",
    "theme": "System",  # System, Dark, Light
    "color_theme": "blue" # blue, green, dark-blue
}

def load_config() -> Dict[str, Any]:
    """
    Loads the configuration from config.json.
    If the file doesn't exist, creates it with default values.
    Returns the configuration dictionary.
    """
    if not os.path.exists(CONFIG_FILE):
        return save_config(DEFAULT_CONFIG)
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with default config to ensure all keys exist
            # This handles cases where new config keys are added in updates
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
    except (json.JSONDecodeError, IOError):
        # If file is corrupted, return default and maybe backup/overwrite?
        # For now, just return default to be safe, maybe log a warning if we had logging
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves the configuration to config.json.
    Returns the saved configuration.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except IOError:
        pass # Handle write error appropriately in a real app
    return config

def get_config_value(key: str, default: Any = None) -> Any:
    """Helper to get a single config value."""
    config = load_config()
    return config.get(key, default)

def update_config_value(key: str, value: Any):
    """Helper to update a single config value."""
    config = load_config()
    config[key] = value
    save_config(config)
