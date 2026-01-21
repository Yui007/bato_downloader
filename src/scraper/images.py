"""
Image URL extraction from bato.to chapter pages.
"""

import re
import requests
from typing import List

from ..logger import get_logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    "Referer": "https://xbat.tv/",
}

# Regex pattern for xbat.tv image CDN (i*.zfs*.com/media/)
IMG_REGEX = re.compile(
    r"https://i\d+\.(?:zfs\d+)\.com/media/[^\"']+?\.(?:webp|jpg|png)"
)


def extract_image_urls(chapter_url: str) -> List[str]:
    """
    Extract all image URLs from an xbat.tv chapter page.
    
    Args:
        chapter_url: The chapter page URL
    
    Returns:
        List of image URLs in page order
    
    Raises:
        requests.RequestException: If the request fails
    """
    logger = get_logger()
    logger.debug(f"Extracting images from: {chapter_url}")
    
    resp = requests.get(chapter_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text
    
    # Extract image URLs using the xbat.tv CDN pattern
    img_urls = IMG_REGEX.findall(html)
    # Remove duplicates while preserving order
    img_urls = list(dict.fromkeys(img_urls))
    
    logger.debug(f"Found {len(img_urls)} image URLs")
    
    return img_urls
