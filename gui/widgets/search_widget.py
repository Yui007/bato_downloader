"""
Search widget for finding manga with card-based results.
"""

from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QFrame, QScrollArea, QGridLayout
)
import requests

from src.scraper import SearchResult
from gui.styles import COLORS


class CoverLoaderThread(QThread):
    """Thread to load cover image."""
    finished = pyqtSignal(str, bytes)  # url, image_data
    
    def __init__(self, url: str, result_id: str):
        super().__init__()
        self.url = url
        self.result_id = result_id
    
    def run(self):
        try:
            resp = requests.get(self.url, timeout=10)
            if resp.status_code == 200:
                self.finished.emit(self.result_id, resp.content)
        except:
            pass


class SearchResultCard(QFrame):
    """Card widget for displaying a search result with cover."""
    
    clicked = pyqtSignal(object)  # Emits SearchResult
    
    def __init__(self, result: SearchResult, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.result = result
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet(f"""
            SearchResultCard {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 10px;
            }}
            SearchResultCard:hover {{
                background-color: {COLORS['accent_primary']};
            }}
        """)
        self.setFixedHeight(130)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)
        
        # Cover image placeholder
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(70, 100)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 5px;
                color: {COLORS['text_muted']};
                font-size: 10px;
            }}
        """)
        self.cover_label.setText("...")
        layout.addWidget(self.cover_label)
        
        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        # Title
        title_label = QLabel(self.result.name)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                background: transparent;
            }}
        """)
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)
        
        # Authors
        if self.result.authors:
            authors_text = ", ".join(self.result.authors[:3])
            if len(self.result.authors) > 3:
                authors_text += " +"
            authors_label = QLabel(f"by {authors_text}")
            authors_label.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 12px; background: transparent; }}")
            info_layout.addWidget(authors_label)
        
        # Genres (first few)
        if self.result.genres:
            genres_text = ", ".join(self.result.genres[:4])
            if len(self.result.genres) > 4:
                genres_text += " +"
            genres_label = QLabel(genres_text.replace("_", " ").title())
            genres_label.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; background: transparent; }}")
            info_layout.addWidget(genres_label)
        
        # Latest chapter
        if self.result.latest_chapter:
            chapter_label = QLabel(f"📚 {self.result.latest_chapter}")
            chapter_label.setStyleSheet(f"QLabel {{ color: {COLORS['accent_secondary']}; font-size: 11px; background: transparent; }}")
            info_layout.addWidget(chapter_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)
        
        # Score badge (if available)
        if self.result.score and self.result.score > 0:
            score_label = QLabel(f"⭐ {self.result.score:.1f}")
            score_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['warning']};
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                }}
            """)
            layout.addWidget(score_label)
    
    def set_cover(self, image_data: bytes):
        """Set cover image from data."""
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data):
            scaled = pixmap.scaled(
                70, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled)
        else:
            self.cover_label.setText("N/A")
    
    def mousePressEvent(self, event):
        """Handle click on card."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.result)
        super().mousePressEvent(event)


class SearchWidget(QWidget):
    """Search screen with input and card-based results."""
    
    manga_selected = pyqtSignal(str)  # Emits manga URL from search results
    url_entered = pyqtSignal(str)  # Emits manga URL from direct URL input
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.results: List[SearchResult] = []
        self.cover_threads: List[CoverLoaderThread] = []
        self.result_cards: dict = {}  # id -> card
        self.current_page = 1
        self.current_query = ""
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🔍 Search Manga")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(header)
        
        # Search bar container
        search_container = QHBoxLayout()
        search_container.setSpacing(10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter manga name (e.g., Solo Leveling)")
        self.search_input.setMinimumHeight(45)
        self.search_input.returnPressed.connect(self._on_search)
        search_container.addWidget(self.search_input)
        
        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setMinimumHeight(45)
        self.search_btn.setMinimumWidth(120)
        self.search_btn.clicked.connect(self._on_search)
        search_container.addWidget(self.search_btn)
        
        layout.addLayout(search_container)
        
        # Divider with "OR"
        divider_layout = QHBoxLayout()
        divider_layout.setSpacing(15)
        
        left_line = QFrame()
        left_line.setFrameShape(QFrame.Shape.HLine)
        left_line.setStyleSheet(f"background-color: {COLORS['border']};")
        left_line.setFixedHeight(1)
        divider_layout.addWidget(left_line)
        
        or_label = QLabel("OR")
        or_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: 600;")
        divider_layout.addWidget(or_label)
        
        right_line = QFrame()
        right_line.setFrameShape(QFrame.Shape.HLine)
        right_line.setStyleSheet(f"background-color: {COLORS['border']};")
        right_line.setFixedHeight(1)
        divider_layout.addWidget(right_line)
        
        layout.addLayout(divider_layout)
        
        # URL input section
        url_container = QHBoxLayout()
        url_container.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste manga URL (e.g., https://xbat.tv/title/81514-solo-leveling-official)")
        self.url_input.setMinimumHeight(45)
        self.url_input.returnPressed.connect(self._on_url_load)
        url_container.addWidget(self.url_input)
        
        self.load_url_btn = QPushButton("Load URL")
        self.load_url_btn.setMinimumHeight(45)
        self.load_url_btn.setMinimumWidth(120)
        self.load_url_btn.clicked.connect(self._on_url_load)
        url_container.addWidget(self.load_url_btn)
        
        layout.addLayout(url_container)
        
        # Results label
        self.results_label = QLabel("Search by name or paste a manga URL directly")
        self.results_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self.results_label)
        
        # Results scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        
        # Container for result cards
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(10)
        self.results_layout.setContentsMargins(10, 10, 10, 10)
        self.results_layout.addStretch()
        
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area, 1)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(15)
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setMinimumWidth(100)
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self._on_prev_page)
        pagination_layout.addWidget(self.prev_btn)
        
        pagination_layout.addStretch()
        
        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        pagination_layout.addWidget(self.page_label)
        
        pagination_layout.addStretch()
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setMinimumWidth(100)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._on_next_page)
        pagination_layout.addWidget(self.next_btn)
        
        self.pagination_container = QWidget()
        self.pagination_container.setLayout(pagination_layout)
        self.pagination_container.hide()  # Hidden until search results
        layout.addWidget(self.pagination_container)
        
        # Loading indicator (hidden by default)
        self.loading_label = QLabel("Searching...")
        self.loading_label.setStyleSheet(f"""
            color: {COLORS['accent_primary']};
            font-size: 16px;
        """)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
    
    def _on_search(self):
        """Handle search button click."""
        query = self.search_input.text().strip()
        if query:
            self.current_query = query
            self.current_page = 1
            self.search_requested(query, page=1)
    
    def _on_prev_page(self):
        """Go to previous page."""
        if self.current_page > 1 and self.current_query:
            self.current_page -= 1
            self.search_requested(self.current_query, page=self.current_page)
    
    def _on_next_page(self):
        """Go to next page."""
        if self.current_query:
            self.current_page += 1
            self.search_requested(self.current_query, page=self.current_page)
    
    def _on_url_load(self):
        """Handle URL load button click."""
        url = self.url_input.text().strip()
        if url:
            # Validate it looks like a xbat URL
            if 'xbat' in url.lower() and '/title/' in url:
                self.url_entered.emit(url)
            else:
                self.results_label.setText("Invalid URL. Please enter a valid xbat.tv manga URL.")
    
    def search_requested(self, query: str, page: int = 1):
        """Override this or connect to signal."""
        pass  # Will be connected in main window
    
    def set_loading(self, loading: bool):
        """Show/hide loading state."""
        self.search_btn.setEnabled(not loading)
        self.search_input.setEnabled(not loading)
        if loading:
            self.loading_label.show()
            self.scroll_area.hide()
        else:
            self.loading_label.hide()
            self.scroll_area.show()
    
    def display_results(self, results: List[SearchResult]):
        """Display search results as cards."""
        self.results = results
        self.result_cards = {}
        
        # Cancel any pending cover loads
        for thread in self.cover_threads:
            if thread.isRunning():
                thread.terminate()
        self.cover_threads = []
        
        # Clear previous results
        while self.results_layout.count() > 1:  # Keep the stretch
            item = self.results_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Update pagination
        self.page_label.setText(f"Page {self.current_page}")
        self.prev_btn.setEnabled(self.current_page > 1)
        
        if not results:
            self.results_label.setText("No manga found. Try a different search term or next page.")
            self.next_btn.setEnabled(False)
            self.pagination_container.show()
            return
        
        self.results_label.setText(f"Found {len(results)} manga on page {self.current_page}:")
        self.next_btn.setEnabled(len(results) >= 30)  # Enable if full page
        self.pagination_container.show()
        
        for result in results:
            card = SearchResultCard(result)
            card.clicked.connect(self._on_card_clicked)
            self.results_layout.insertWidget(self.results_layout.count() - 1, card)
            self.result_cards[result.id] = card
            
            # Load cover image asynchronously
            if result.cover_url:
                thread = CoverLoaderThread(result.cover_url, result.id)
                thread.finished.connect(self._on_cover_loaded)
                thread.start()
                self.cover_threads.append(thread)
    
    def _on_cover_loaded(self, result_id: str, image_data: bytes):
        """Handle cover image loaded."""
        if result_id in self.result_cards:
            self.result_cards[result_id].set_cover(image_data)
    
    def _on_card_clicked(self, result: SearchResult):
        """Handle card click."""
        self.manga_selected.emit(result.full_url)
    
    def display_error(self, error: str):
        """Display error message."""
        self.results_label.setText(f"Error: {error}")
        
        # Clear results
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
