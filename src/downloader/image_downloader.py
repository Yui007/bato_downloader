"""
Image downloading with retry logic and connection pooling.
"""

import os
import time
import requests
from typing import Optional, Callable
from pathlib import Path

from ..logger import get_logger
from ..config import get_config

# Shared session for connection pooling
_session: Optional[requests.Session] = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
}


def get_session() -> requests.Session:
    """Get or create a shared requests session for connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(HEADERS)
        # Configure connection pool
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=0  # We handle retries ourselves
        )
        _session.mount('http://', adapter)
        _session.mount('https://', adapter)
    return _session


def download_image(
    url: str,
    output_path: str | Path,
    max_retries: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> bool:
    """
    Download a single image with retry logic and exponential backoff.
    
    Args:
        url: Image URL to download
        output_path: Path to save the image
        max_retries: Maximum retry attempts (default from config)
        progress_callback: Optional callback(bytes_downloaded, total_bytes)
    
    Returns:
        True if download succeeded, False otherwise
    """
    logger = get_logger()
    config = get_config()
    
    if max_retries is None:
        max_retries = config.max_image_retries
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    session = get_session()
    retry_delays = [1, 3, 7]  # Seconds between retries
    
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"Downloading image (attempt {attempt + 1}): {url}")
            
            resp = session.get(url, timeout=30, stream=True)
            resp.raise_for_status()
            
            # Get total size if available
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            # Write to file
            with open(output_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            logger.debug(f"Successfully downloaded: {output_path.name}")
            return True
            
        except requests.RequestException as e:
            logger.warning(f"Download failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
            
            if attempt < max_retries:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                logger.debug(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to download after {max_retries + 1} attempts: {url}")
                return False
    
    return False


def reset_session() -> None:
    """Reset the shared session (useful for cleanup)."""
    global _session
    if _session is not None:
        _session.close()
        _session = None
