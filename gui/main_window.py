"""
Main application window with navigation.
"""

from typing import Optional, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QFrame, QLabel,
    QMessageBox
)

from gui.styles import MAIN_STYLESHEET, SIDEBAR_STYLE, COLORS
from gui.widgets import SearchWidget, MangaWidget, SettingsWidget, DownloadWidget
from gui.workers import SearchWorker, ScraperWorker, CoverWorker, DownloadWorker
from src.scraper import MangaInfo, Chapter
from src.config import get_config
from src.logger import setup_logger


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        config = get_config()
        setup_logger(config.enable_detailed_logs)
        
        # Current state
        self.current_manga_info: Optional[MangaInfo] = None
        self.current_chapters: List[Chapter] = []
        self.current_worker = None
        self.download_worker = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Bato Downloader")
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)
        
        # Apply stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)
        
        # Create pages
        self.search_page = SearchWidget()
        self.manga_page = MangaWidget()
        self.downloads_page = DownloadWidget()
        self.settings_page = SettingsWidget()
        
        self.content_stack.addWidget(self.search_page)
        self.content_stack.addWidget(self.manga_page)
        self.content_stack.addWidget(self.downloads_page)
        self.content_stack.addWidget(self.settings_page)
        
        # Set default page
        self.content_stack.setCurrentWidget(self.search_page)
        self.search_btn.setChecked(True)
    
    def _create_sidebar(self) -> QFrame:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Title
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border: none;
                padding: 20px;
            }}
        """)
        title_layout = QVBoxLayout(title_frame)
        
        logo = QLabel("📚")
        logo.setStyleSheet("font-size: 32px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(logo)
        
        title = QLabel("Bato Downloader")
        title.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        layout.addWidget(title_frame)
        
        # Navigation buttons
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setCheckable(True)
        self.search_btn.clicked.connect(lambda: self._navigate_to(0))
        layout.addWidget(self.search_btn)
        
        self.manga_btn = QPushButton("📖 Manga")
        self.manga_btn.setCheckable(True)
        self.manga_btn.clicked.connect(lambda: self._navigate_to(1))
        layout.addWidget(self.manga_btn)
        
        self.downloads_btn = QPushButton("⬇️ Downloads")
        self.downloads_btn.setCheckable(True)
        self.downloads_btn.clicked.connect(lambda: self._navigate_to(2))
        layout.addWidget(self.downloads_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(lambda: self._navigate_to(3))
        layout.addWidget(self.settings_btn)
        
        layout.addStretch()
        
        # Version
        version = QLabel("v1.0.0")
        version.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            padding: 10px;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        return sidebar
    
    def _connect_signals(self):
        """Connect all widget signals."""
        # Search page
        self.search_page.search_requested = self._on_search
        self.search_page.manga_selected.connect(self._on_manga_selected)
        self.search_page.url_entered.connect(self._on_manga_selected)  # Direct URL also goes to manga page
        
        # Manga page
        self.manga_page.back_requested.connect(lambda: self._navigate_to(0))
        self.manga_page.download_requested.connect(self._on_download_requested)
        
        # Downloads page
        self.downloads_page.cancel_btn.clicked.connect(self._on_cancel_downloads)
    
    def _navigate_to(self, index: int):
        """Navigate to a page by index."""
        self.content_stack.setCurrentIndex(index)
        
        # Update button states
        buttons = [self.search_btn, self.manga_btn, self.downloads_btn, self.settings_btn]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
    
    def _on_search(self, query: str, page: int = 1):
        """Handle search request."""
        self.search_page.set_loading(True)
        
        self.current_worker = SearchWorker(query, page=page)
        self.current_worker.finished.connect(self._on_search_finished)
        self.current_worker.error.connect(self._on_search_error)
        self.current_worker.start()
    
    def _on_search_finished(self, results):
        """Handle search results."""
        self.search_page.set_loading(False)
        self.search_page.display_results(results)
    
    def _on_search_error(self, error: str):
        """Handle search error."""
        self.search_page.set_loading(False)
        self.search_page.display_error(error)
    
    def _on_manga_selected(self, url: str):
        """Handle manga selection from search results."""
        self._navigate_to(1)
        self.manga_page.clear()
        self.manga_page.set_loading(True)
        
        self.current_worker = ScraperWorker(url)
        self.current_worker.info_ready.connect(self._on_manga_info_ready)
        self.current_worker.chapters_ready.connect(self._on_chapters_ready)
        self.current_worker.error.connect(self._on_manga_error)
        self.current_worker.start()
    
    def _on_manga_info_ready(self, info: MangaInfo):
        """Handle manga info loaded."""
        self.current_manga_info = info
        self.manga_page.set_manga_info(info)
        
        # Load cover image
        if info.cover_url:
            cover_worker = CoverWorker(info.cover_url)
            cover_worker.finished.connect(self.manga_page.set_cover)
            cover_worker.start()
            # Keep reference to prevent garbage collection
            self._cover_worker = cover_worker
    
    def _on_chapters_ready(self, chapters: List[Chapter]):
        """Handle chapters loaded."""
        self.current_chapters = chapters
        self.manga_page.set_chapters(chapters)
        self.manga_page.set_loading(False)
    
    def _on_manga_error(self, error: str):
        """Handle manga loading error."""
        self.manga_page.set_loading(False)
        QMessageBox.warning(self, "Error", f"Failed to load manga: {error}")
    
    def _on_download_requested(self, chapters: List[Chapter]):
        """Handle download request."""
        if not self.current_manga_info:
            return
        
        # Navigate to downloads page
        self._navigate_to(2)
        
        # Setup download UI
        self.downloads_page.start_downloads(chapters, self.current_manga_info.title)
        
        # Start download worker
        self.download_worker = DownloadWorker(chapters, self.current_manga_info)
        self.download_worker.chapter_started.connect(self.downloads_page.on_chapter_started)
        self.download_worker.chapter_progress.connect(self.downloads_page.on_chapter_progress)
        self.download_worker.chapter_completed.connect(self.downloads_page.on_chapter_completed)
        self.download_worker.all_completed.connect(self.downloads_page.on_all_completed)
        self.download_worker.error.connect(self._on_download_error)
        self.download_worker.start()
    
    def _on_cancel_downloads(self):
        """Handle cancel downloads button."""
        if self.download_worker:
            self.download_worker.cancel()
    
    def _on_download_error(self, error: str):
        """Handle download error."""
        QMessageBox.warning(self, "Download Error", f"An error occurred: {error}")
    
    def closeEvent(self, event):
        """Handle window close."""
        # Cancel any running workers
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.download_worker.wait(1000)
        
        event.accept()
