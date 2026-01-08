"""
Logging configuration for Bato Downloader.
"""

import logging
import sys
from typing import Optional

# Logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(enable_detailed: bool = False) -> logging.Logger:
    """
    Setup and return the application logger.
    
    Args:
        enable_detailed: If True, enables DEBUG level logging. Otherwise, WARNING only.
    """
    global _logger
    
    if _logger is not None:
        # Update existing logger level
        level = logging.DEBUG if enable_detailed else logging.WARNING
        _logger.setLevel(level)
        for handler in _logger.handlers:
            handler.setLevel(level)
        return _logger
    
    # Create new logger
    _logger = logging.getLogger("bato-downloader")
    level = logging.DEBUG if enable_detailed else logging.WARNING
    _logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    _logger.addHandler(handler)
    return _logger


def get_logger() -> logging.Logger:
    """Get the application logger, creating it if necessary."""
    global _logger
    if _logger is None:
        _logger = setup_logger(False)
    return _logger
