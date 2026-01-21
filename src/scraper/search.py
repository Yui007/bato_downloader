"""
Search functionality for bato.to using GraphQL API.
"""

import requests
from dataclasses import dataclass, field
from typing import List, Optional

from ..logger import get_logger

API_URL = "https://xbat.tv/ap2/"

HEADERS = {
    "Content-Type": "application/json",
    "x-apollo-operation-name": "get_search_comic",
}


@dataclass
class SearchResult:
    """Search result data class with enhanced info."""
    id: str
    name: str
    url_path: str
    cover_url: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    authors: List[str] = field(default_factory=list)
    artists: List[str] = field(default_factory=list)
    score: Optional[float] = None
    follows: Optional[int] = None
    latest_chapter: Optional[str] = None
    
    @property
    def full_url(self) -> str:
        """Get the full URL for the manga."""
        if self.url_path.startswith('/'):
            return f"https://xbat.tv{self.url_path}"
        return f"https://xbat.tv/{self.url_path}"


def search_manga(query: str, page: int = 1, size: int = 30) -> List[SearchResult]:
    """
    Search for manga on bato.to.
    
    Args:
        query: Search query string
        page: Page number (1-indexed)
        size: Number of results per page
    
    Returns:
        List of SearchResult objects
    
    Raises:
        requests.RequestException: If the request fails
    """
    logger = get_logger()
    logger.debug(f"Searching for: {query} (page={page}, size={size})")
    
    payload = {
        "query": """
        query get_search_comic($select: Search_Comic_Select) {
          get_search_comic(select: $select) {
            items {
              id
              data {
                name
                urlPath
                urlCover600
                urlCoverOri
                genres
                authors
                artists
                score_val
                follows
                reviews
                comments_total
                chapterNode_up_to {
                  id
                  data {
                    dname
                    urlPath
                    isFinal
                  }
                }
              }
            }
          }
        }
        """,
        "variables": {
            "select": {
                "word": query,
                "size": size,
                "page": page
            }
        }
    }
    
    try:
        with requests.Session() as session:
            resp = session.post(API_URL, json=payload, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
    except requests.RequestException as e:
        logger.error(f"Search request failed: {e}")
        raise
    
    results = []
    items = data.get("data", {}).get("get_search_comic", {}).get("items", [])
    
    for item in items:
        item_data = item.get("data", {})
        
        # Get cover URL (prefer 600px version)
        cover_url = item_data.get("urlCover600") or item_data.get("urlCoverOri")
        if cover_url and not cover_url.startswith("http"):
            cover_url = f"https://xbat.tv{cover_url}"
        
        # Get latest chapter info
        latest_chap = item_data.get("chapterNode_up_to", {}).get("data", {})
        latest_chapter = latest_chap.get("dname") if latest_chap else None
        
        results.append(SearchResult(
            id=item.get("id", ""),
            name=item_data.get("name", "Unknown"),
            url_path=item_data.get("urlPath", ""),
            cover_url=cover_url,
            genres=item_data.get("genres", []),
            authors=item_data.get("authors", []),
            artists=item_data.get("artists", []),
            score=item_data.get("score_val"),
            follows=item_data.get("follows"),
            latest_chapter=latest_chapter
        ))
    
    logger.debug(f"Found {len(results)} search results")
    
    return results
