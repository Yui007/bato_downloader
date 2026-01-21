"""
Configuration management for Bato Downloader.
Stores settings in a JSON config file.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

# Config file location - in project directory
CONFIG_DIR = Path(__file__).parent.parent  # bato-downloader root
CONFIG_FILE = CONFIG_DIR / "config.json"

# Download format options
DownloadFormat = Literal["images", "pdf", "cbz"]


@dataclass
class Config:
    """Application configuration settings."""
    
    # Download settings
    download_format: DownloadFormat = "images"
    keep_images_after_conversion: bool = True
    output_directory: str = ""  # Empty means project folder, set dynamically
    
    # Concurrency settings
    concurrent_chapters: int = 3
    concurrent_images: int = 5
    
    # Retry settings
    max_chapter_retries: int = 3
    max_image_retries: int = 3
    
    # CLI settings
    cli_chapters_display_limit: int = 0  # 0 = show all chapters
    
    # Logging
    enable_detailed_logs: bool = False
    
    def save(self) -> None:
        """Save configuration to JSON file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from JSON file, or create default if not exists."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                # Invalid config, return default
                return cls()
        return cls()


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def save_config() -> None:
    """Save the global configuration."""
    global _config
    if _config is not None:
        _config.save()


def reset_config() -> Config:
    """Reset configuration to defaults."""
    global _config
    _config = Config()
    _config.save()
    return _config
