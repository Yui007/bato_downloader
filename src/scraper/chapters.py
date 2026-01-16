"""
Chapter listing extraction from bato.to.
"""

import re
import requests
from dataclasses import dataclass
from typing import List, Optional

from ..logger import get_logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
}


@dataclass
class Chapter:
    """Chapter data class."""
    url: str
    number: str
    title: Optional[str]
    
    @property
    def display_name(self) -> str:
        """Get display name for the chapter."""
        if self.title:
            return f"{self.number}: {self.title}"
        return self.number


def fetch_chapters(manga_url: str) -> List[Chapter]:
    """
    Fetch all chapters from a bato.to manga page.
    
    Args:
        manga_url: The manga page URL
    
    Returns:
        List of Chapter objects, ordered from first to last
    
    Raises:
        requests.RequestException: If the request fails
    """
    logger = get_logger()
    logger.debug(f"Fetching chapters from: {manga_url}")
    
    # Ensure we're fetching from the chapters section

    # NOTE:
    # bato.si paginates chapter listings in batches of 100 using the `start` query parameter.
    # While `start=1`, `start=101`, etc. return paginated results, testing shows that
    # `start=-1` returns the full chapter list in a single response.
    
    manga_url = f"{manga_url.split('?', 1)[0]}?start=-1"
    
    resp = requests.get(manga_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text
    
    # Regex pattern for chapters
    chapter_pattern = re.compile(
        r'<div class="space-x-1">.*?'
        r'<a href="([^"]+)"[^>]*>([^<]+)</a>'  # chapter number
        r'(?:<span[^>]*>:\s*([^<]+)</span>)?',  # optional chapter title
        re.DOTALL
    )
    
    chapters = []
    for match in chapter_pattern.finditer(html):
        url_path = match.group(1)
        number = match.group(2).strip()
        title = match.group(3).strip() if match.group(3) else None
        
        # Skip version numbers and non-chapter entries
        # These typically start with 'v' followed by numbers (e.g., v20251008)
        if re.match(r'^v\d+$', number, re.IGNORECASE):
            continue
        
        # Build full URL
        if url_path.startswith('/'):
            full_url = f"https://bato.si{url_path}"
        else:
            full_url = url_path
        
        chapters.append(Chapter(
            url=full_url,
            number=number,
            title=title
        ))
    
    logger.debug(f"Found {len(chapters)} chapters")
    
    # Reverse to get oldest first (optional, depending on preference)
    # chapters.reverse()
    
    return chapters
