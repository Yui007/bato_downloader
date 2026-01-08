"""
QThread workers for background operations.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from src.scraper import MangaInfo, SearchResult, Chapter
from src.scraper import fetch_manga_info, fetch_chapters, search_manga
from src.downloader.chapter_downloader import ChapterDownloader, DownloadProgress
from src.downloader.converter import images_to_pdf, images_to_cbz, cleanup_images
from src.config import get_config


class SearchWorker(QThread):
    """Background worker for manga search."""
    
    finished = pyqtSignal(list)  # List of SearchResult
    error = pyqtSignal(str)
    
    def __init__(self, query: str, page: int = 1, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.query = query
        self.page = page
    
    def run(self):
        try:
            results = search_manga(self.query, page=self.page)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class ScraperWorker(QThread):
    """Background worker for fetching manga info and chapters."""
    
    info_ready = pyqtSignal(object)  # MangaInfo
    chapters_ready = pyqtSignal(list)  # List of Chapter
    error = pyqtSignal(str)
    
    def __init__(self, url: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.url = url
    
    def run(self):
        try:
            # Fetch manga info
            info = fetch_manga_info(self.url)
            self.info_ready.emit(info)
            
            # Fetch chapters
            chapters = fetch_chapters(self.url)
            self.chapters_ready.emit(chapters)
            
        except Exception as e:
            self.error.emit(str(e))


class CoverWorker(QThread):
    """Background worker for loading cover images."""
    
    finished = pyqtSignal(bytes)  # Image data
    error = pyqtSignal(str)
    
    def __init__(self, url: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.url = url
    
    def run(self):
        try:
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(self.url, headers=headers, timeout=30)
            resp.raise_for_status()
            self.finished.emit(resp.content)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    """Background worker for downloading chapters with concurrency."""
    
    # Progress signals
    chapter_started = pyqtSignal(str, int)  # chapter_number, total_images
    chapter_progress = pyqtSignal(str, int, int)  # chapter_number, downloaded, total
    chapter_completed = pyqtSignal(str, bool)  # chapter_number, success
    all_completed = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(
        self,
        chapters: List[Chapter],
        manga_info: MangaInfo,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self.chapters = chapters
        self.manga_info = manga_info
        self._cancelled = False
    
    def cancel(self):
        """Cancel the download operation."""
        self._cancelled = True
    
    def run(self):
        try:
            config = get_config()
            output_dir = Path(config.output_directory)
            
            # Download chapters with concurrency
            with ThreadPoolExecutor(max_workers=config.concurrent_chapters) as executor:
                futures = {}
                
                for chapter in self.chapters:
                    if self._cancelled:
                        break
                    
                    future = executor.submit(
                        self._download_single_chapter,
                        chapter,
                        output_dir
                    )
                    futures[future] = chapter
                
                for future in as_completed(futures):
                    if self._cancelled:
                        break
                    
                    chapter = futures[future]
                    try:
                        success, chapter_folder = future.result()
                        
                        # Convert if needed
                        if success and config.download_format != 'images':
                            self._convert_chapter(chapter, chapter_folder)
                        
                        self.chapter_completed.emit(chapter.number, success)
                    except Exception as e:
                        self.chapter_completed.emit(chapter.number, False)
            
            self.all_completed.emit()
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _download_single_chapter(self, chapter: Chapter, output_dir: Path):
        """Download a single chapter."""
        def progress_callback(progress: DownloadProgress):
            if progress.status == 'downloading':
                if progress.downloaded_images == 0:
                    self.chapter_started.emit(
                        progress.chapter_number,
                        progress.total_images
                    )
                self.chapter_progress.emit(
                    progress.chapter_number,
                    progress.downloaded_images,
                    progress.total_images
                )
        
        downloader = ChapterDownloader(progress_callback)
        return downloader.download_chapter(
            chapter,
            output_dir,
            self.manga_info.title
        )
    
    def _convert_chapter(self, chapter: Chapter, chapter_folder: Path):
        """Convert chapter to PDF or CBZ."""
        config = get_config()
        
        # Determine output filename
        safe_title = chapter_folder.parent.name
        safe_chapter = chapter_folder.name
        
        if config.download_format == 'pdf':
            output_file = chapter_folder.parent / f"{safe_chapter}.pdf"
            success = images_to_pdf(chapter_folder, output_file)
        else:  # cbz
            output_file = chapter_folder.parent / f"{safe_chapter}.cbz"
            success = images_to_cbz(
                chapter_folder,
                output_file,
                self.manga_info,
                chapter
            )
        
        # Cleanup images if conversion successful and not keeping images
        if success and not config.keep_images_after_conversion:
            cleanup_images(chapter_folder)
