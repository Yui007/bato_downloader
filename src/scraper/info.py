"""
Manga information extraction from bato.to.
"""

import re
import requests
from dataclasses import dataclass
from typing import Optional, List

from ..logger import get_logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
}


@dataclass
class MangaInfo:
    """Manga information data class."""
    title: str
    authors: List[str]
    status: Optional[str]
    genres: List[str]
    description: Optional[str]
    cover_url: Optional[str]
    views: Optional[str]
    url: str


def fetch_manga_info(url: str) -> MangaInfo:
    """
    Fetch manga information from a bato.to manga page.
    
    Args:
        url: The manga page URL (e.g., https://xbat.tv/title/81514-solo-leveling-official)
    
    Returns:
        MangaInfo object with extracted data
    
    Raises:
        requests.RequestException: If the request fails
    """
    logger = get_logger()
    logger.debug(f"Fetching manga info from: {url}")
    
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text
    
    # 1. Title (allow optional HTML comments inside <a>)
    title_match = re.search(
        r'<h3[^>]*>\s*<a [^>]*>(?:<!--.*?-->\s*)*([^<]+)',
        html,
        re.DOTALL
    )
    title = title_match.group(1).strip() if title_match else "Unknown Title"
    logger.debug(f"Extracted title: {title}")
    
    # 2. Authors
    authors = re.findall(r'<a href="/author\?name=[^"]+"[^>]*>([^<]+)</a>', html)
    logger.debug(f"Extracted authors: {authors}")
    
    # 3. Status (Ongoing / Completed)
    status_match = re.search(
        r'Bato Upload Status:</span>\s*<span class="font-bold uppercase text-success">([^<]+)</span>',
        html
    )
    status = status_match.group(1).strip() if status_match else None
    logger.debug(f"Extracted status: {status}")
    
    # 4. Genres - find the Genres div and extract spans
    genres_div_match = re.search(
        r'<div class="flex items-center flex-wrap"[^>]*>\s*<b[^>]*>Genres:</b>(.*?)</div>',
        html,
        re.DOTALL
    )
    genres = []
    if genres_div_match:
        genres_div = genres_div_match.group(1)
        # Try bold spans first (primary genres)
        genres = re.findall(r'<span class="whitespace-nowrap[^"]*font-bold[^"]*"[^>]*>(?:<!--.*?-->)*\s*([^<]+)', genres_div)
        # Fallback: get all whitespace-nowrap spans
        if not genres:
            genres = re.findall(r'<span class="whitespace-nowrap[^"]*"[^>]*>(?:<!--.*?-->)*\s*([^<]+)', genres_div)
    # Clean and filter genres
    genres = [g.strip() for g in genres if g.strip() and len(g.strip()) > 1]
    logger.debug(f"Extracted genres: {genres}")
    
    # 5. Description - try multiple patterns
    description = None
    # Pattern 1: EN description
    desc_match = re.search(
        r'<b>EN</b></div>\s*<div class="limit-html-p">(.*?)</div>',
        html,
        re.DOTALL
    )
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        # Pattern 2: limit-html prose div
        desc_match = re.search(
            r'<div class="limit-html prose[^"]*"[^>]*>\s*<div class="limit-html-p">(.*?)</div>',
            html,
            re.DOTALL
        )
        if desc_match:
            description = desc_match.group(1).strip()
    # Clean HTML tags and comments from description
    if description:
        description = re.sub(r'<!--.*?-->', '', description)
        description = re.sub(r'<[^>]+>', '', description).strip()
    logger.debug(f"Extracted description: {description[:100] if description else None}...")
    
    # 6. Cover image - try multiple patterns
    cover_url = None
    # Pattern 1: /ap1/xfs/attachs/ path
    covers = re.findall(r'<img src="(/ap1/xfs/attachs/[^"]+)"', html)
    if covers:
        cover_url = f"https://xbat.tv{covers[0]}"
    else:
        # Pattern 2: /media/ampi/ path
        covers = re.findall(r'<img src="(/media/ampi/[^"]+)"', html)
        if covers:
            cover_url = f"https://xbat.tv{covers[0]}"
        else:
            # Pattern 3: /media/mbim/ path
            covers = re.findall(r'<img src="(/media/mbim/[^"]+)"', html)
            if covers:
                cover_url = f"https://xbat.tv{covers[0]}"
    logger.debug(f"Extracted cover URL: {cover_url}")
    
    # 7. Views
    views_match = re.search(r'Total:\s*([\d\.K]+)', html)
    views = views_match.group(1) if views_match else None
    logger.debug(f"Extracted views: {views}")
    
    return MangaInfo(
        title=title,
        authors=authors,
        status=status,
        genres=genres,
        description=description,
        cover_url=cover_url,
        views=views,
        url=url
    )
