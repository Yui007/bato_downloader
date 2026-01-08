"""
Image URL extraction from bato.to chapter pages.
"""

import re
import requests
from typing import List

from ..logger import get_logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
}

# List of all MB* image CDN servers
IMAGE_SERVERS = [
    "mbcej.org", "mbdny.org", "mbeaj.org", "mbfpu.org", "mbhiz.org",
    "mbimg.org", "mbiny.org", "mbmyj.org", "mbopg.org", "mbqgu.org",
    "mbqtj.org", "mbrtz.org", "mbtba.org", "mbtmv.org", "mbuul.org",
    "mbwbm.org", "mbwnp.org", "mbwww.org", "mbxma.org", "mbzcp.org",
    "mbznp.org"
]


def extract_image_urls(chapter_url: str) -> List[str]:
    """
    Extract all image URLs from a bato.to chapter page.
    
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
    
    # Build regex pattern for all MB* servers
    server_pattern = "|".join([s.replace(".", r"\.") for s in IMAGE_SERVERS])
    # Match both nXX and kXX subdomains
    regex_pattern = rf'https://[nk]\d+\.(?:{server_pattern})/media/[^"\', ]+?\.(?:webp|jpe?g|png|gif)'
    
    # Extract image URLs
    img_urls = re.findall(regex_pattern, html)
    # Remove duplicates while preserving order
    img_urls = list(dict.fromkeys(img_urls))
    
    logger.debug(f"Found {len(img_urls)} raw image URLs")
    
    # Fix kXX -> nXX for all URLs (some CDN subdomains use k instead of n)
    fixed_urls = []
    for url in img_urls:
        fixed_url = re.sub(r"https://k(\d+)\.", r"https://n\1.", url)
        fixed_urls.append(fixed_url)
    
    logger.debug(f"Returning {len(fixed_urls)} fixed image URLs")
    
    return fixed_urls
