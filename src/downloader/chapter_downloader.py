"""
Chapter downloading with concurrent image downloads and retry logic.
"""

import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, List, Tuple

from ..logger import get_logger
from ..config import get_config
from ..scraper.chapters import Chapter
from ..scraper.images import extract_image_urls
from .image_downloader import download_image


@dataclass
class DownloadProgress:
    """Progress information for a chapter download."""
    chapter_number: str
    total_images: int
    downloaded_images: int
    failed_images: int
    status: str  # 'pending', 'downloading', 'completed', 'failed'


class ChapterDownloader:
    """
    Downloads manga chapters with concurrent image downloads.
    """
    
    def __init__(
        self,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ):
        """
        Initialize the chapter downloader.
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.progress_callback = progress_callback
        self.logger = get_logger()
        self._cancelled = False
    
    def cancel(self) -> None:
        """Cancel the current download operation."""
        self._cancelled = True
    
    def reset(self) -> None:
        """Reset cancel state for new downloads."""
        self._cancelled = False
    
    def download_chapter(
        self,
        chapter: Chapter,
        output_dir: str | Path,
        manga_title: str = "Unknown"
    ) -> Tuple[bool, Path]:
        """
        Download a single chapter with all its images.
        
        Args:
            chapter: Chapter to download
            output_dir: Base output directory
            manga_title: Title of the manga (for folder naming)
        
        Returns:
            Tuple of (success: bool, chapter_folder: Path)
        """
        config = get_config()
        self.logger.debug(f"Starting download for: {chapter.display_name}")
        
        # Create chapter folder
        safe_title = self._sanitize_filename(manga_title)
        safe_chapter = self._sanitize_filename(chapter.number)
        chapter_folder = Path(output_dir) / safe_title / f"Chapter {safe_chapter}"
        chapter_folder.mkdir(parents=True, exist_ok=True)
        
        # Update progress
        progress = DownloadProgress(
            chapter_number=chapter.number,
            total_images=0,
            downloaded_images=0,
            failed_images=0,
            status='downloading'
        )
        
        # Retry logic for chapter
        retry_delays = [2, 5, 10]
        max_retries = config.max_chapter_retries
        
        for attempt in range(max_retries + 1):
            try:
                if self._cancelled:
                    progress.status = 'failed'
                    self._notify_progress(progress)
                    return False, chapter_folder
                
                # Extract image URLs
                image_urls = extract_image_urls(chapter.url)
                
                if not image_urls:
                    self.logger.warning(f"No images found for chapter {chapter.number}")
                    progress.status = 'failed'
                    self._notify_progress(progress)
                    return False, chapter_folder
                
                progress.total_images = len(image_urls)
                self._notify_progress(progress)
                
                # Download images concurrently
                success = self._download_images(
                    image_urls,
                    chapter_folder,
                    progress,
                    config.concurrent_images
                )
                
                if success:
                    progress.status = 'completed'
                    self._notify_progress(progress)
                    return True, chapter_folder
                else:
                    raise Exception("Some images failed to download")
                    
            except Exception as e:
                self.logger.warning(f"Chapter download failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries:
                    delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                    self.logger.debug(f"Retrying chapter in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to download chapter after {max_retries + 1} attempts")
                    progress.status = 'failed'
                    self._notify_progress(progress)
                    return False, chapter_folder
        
        return False, chapter_folder
    
    def _download_images(
        self,
        image_urls: List[str],
        output_folder: Path,
        progress: DownloadProgress,
        max_concurrent: int
    ) -> bool:
        """Download all images for a chapter concurrently."""
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {}
            
            for i, url in enumerate(image_urls, start=1):
                if self._cancelled:
                    break
                
                # Determine file extension from URL
                ext = self._get_extension(url)
                filename = output_folder / f"{i:03d}{ext}"
                
                future = executor.submit(download_image, url, filename)
                futures[future] = (i, url)
            
            # Collect results
            for future in as_completed(futures):
                if self._cancelled:
                    break
                
                idx, url = futures[future]
                try:
                    success = future.result()
                    if success:
                        progress.downloaded_images += 1
                    else:
                        progress.failed_images += 1
                except Exception as e:
                    self.logger.error(f"Error downloading image {idx}: {e}")
                    progress.failed_images += 1
                
                self._notify_progress(progress)
        
        return progress.failed_images == 0
    
    def _notify_progress(self, progress: DownloadProgress) -> None:
        """Send progress update to callback if available."""
        if self.progress_callback:
            self.progress_callback(progress)
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Remove invalid characters from filename."""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = sanitized.strip('. ')
        return sanitized or "Unknown"
    
    @staticmethod
    def _get_extension(url: str) -> str:
        """Get file extension from URL."""
        if '.webp' in url:
            return '.webp'
        elif '.png' in url:
            return '.png'
        elif '.gif' in url:
            return '.gif'
        elif '.jpeg' in url or '.jpg' in url:
            return '.jpg'
        return '.webp'  # Default
