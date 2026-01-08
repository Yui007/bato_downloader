"""
Manga details and chapter selection widget.
"""

from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame,
    QSplitter
)

from src.scraper import MangaInfo, Chapter
from gui.styles import COLORS


class MangaWidget(QWidget):
    """Manga details view with chapter selection."""
    
    download_requested = pyqtSignal(list)  # List of Chapter objects
    back_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.manga_info: Optional[MangaInfo] = None
        self.chapters: List[Chapter] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Back button
        back_btn = QPushButton("← Back to Search")
        back_btn.setProperty("class", "secondary")
        back_btn.setMaximumWidth(160)
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Manga info
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(15)
        
        # Cover image
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(200, 280)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-radius: 8px;
        """)
        self.cover_label.setText("Loading...")
        info_layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Title
        self.title_label = QLabel("Loading manga info...")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        info_layout.addWidget(self.title_label)
        
        # Authors
        self.authors_label = QLabel()
        self.authors_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info_layout.addWidget(self.authors_label)
        
        # Status
        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"""
            color: {COLORS['success']};
            font-weight: 600;
        """)
        info_layout.addWidget(self.status_label)
        
        # Genres
        self.genres_label = QLabel()
        self.genres_label.setWordWrap(True)
        self.genres_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        info_layout.addWidget(self.genres_label)
        
        # Views
        self.views_label = QLabel()
        self.views_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        info_layout.addWidget(self.views_label)
        
        # Description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumHeight(150)
        self.description_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 12px;
            padding: 10px;
            background-color: {COLORS['bg_tertiary']};
            border-radius: 6px;
        """)
        info_layout.addWidget(self.description_label)
        
        info_layout.addStretch()
        
        splitter.addWidget(info_frame)
        
        # Right side - Chapters
        chapters_frame = QFrame()
        chapters_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        chapters_layout = QVBoxLayout(chapters_frame)
        chapters_layout.setContentsMargins(20, 20, 20, 20)
        chapters_layout.setSpacing(10)
        
        # Chapters header with count
        self.chapters_header = QLabel("Chapters")
        self.chapters_header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        chapters_layout.addWidget(self.chapters_header)
        
        # Select All / Select None buttons
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setProperty("class", "secondary")
        self.select_all_btn.clicked.connect(self._select_all)
        selection_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.setProperty("class", "secondary")
        self.select_none_btn.clicked.connect(self._select_none)
        selection_layout.addWidget(self.select_none_btn)
        
        selection_layout.addStretch()
        chapters_layout.addLayout(selection_layout)
        
        # Chapters list - using native checkable items
        self.chapters_list = QListWidget()
        self.chapters_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Enable drag selection
        self.chapters_list.itemClicked.connect(self._on_chapter_clicked)  # Toggle on click
        self.chapters_list.itemSelectionChanged.connect(self._on_selection_changed)  # Tick when drag-selected
        self.chapters_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 6px;
                padding: 12px 15px;
                margin: 3px 0;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['accent_primary']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent_primary']};
            }}
        """)
        self.chapters_list.setSpacing(2)
        chapters_layout.addWidget(self.chapters_list, 1)
        
        # Download button
        self.download_btn = QPushButton("⬇️ Download Selected")
        self.download_btn.setMinimumHeight(50)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_gradient_start']},
                    stop:1 {COLORS['accent_gradient_end']});
                font-size: 16px;
                font-weight: 600;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_secondary']},
                    stop:1 #f472b6);
            }}
        """)
        self.download_btn.clicked.connect(self._on_download)
        chapters_layout.addWidget(self.download_btn)
        
        splitter.addWidget(chapters_frame)
        
        # Set splitter sizes
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter, 1)
        
        # Loading overlay
        self.loading_label = QLabel("Loading manga information...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['accent_primary']};
        """)
        self.loading_label.hide()
    
    def set_loading(self, loading: bool):
        """Show/hide loading state."""
        if loading:
            self.loading_label.show()
        else:
            self.loading_label.hide()
    
    def set_manga_info(self, info: MangaInfo):
        """Display manga information."""
        self.manga_info = info
        
        self.title_label.setText(info.title)
        self.authors_label.setText(f"By: {', '.join(info.authors) if info.authors else 'Unknown'}")
        self.status_label.setText(f"Status: {info.status or 'Unknown'}")
        self.genres_label.setText(f"Genres: {', '.join(info.genres) if info.genres else 'N/A'}")
        self.views_label.setText(f"Views: {info.views or 'N/A'}")
        
        # Description (truncate if too long)
        if info.description:
            desc = info.description[:300] + "..." if len(info.description) > 300 else info.description
            self.description_label.setText(desc)
            self.description_label.show()
        else:
            self.description_label.hide()
    
    def set_cover(self, image_data: bytes):
        """Display cover image."""
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data):
            scaled = pixmap.scaled(
                200, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled)
        else:
            self.cover_label.setText("Cover unavailable")
    
    def set_chapters(self, chapters: List[Chapter]):
        """Display chapter list using native checkable items."""
        self.chapters = chapters
        self.chapters_list.clear()
        
        self.chapters_header.setText(f"Chapters ({len(chapters)})")
        
        for chapter in chapters:
            # Create display text
            if chapter.title:
                display_text = f"{chapter.number} - {chapter.title}"
            else:
                display_text = chapter.number
            
            # Create checkable list item
            item = QListWidgetItem(display_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, chapter)  # Store chapter object
            
            self.chapters_list.addItem(item)
    
    def _select_all(self):
        """Select all chapters."""
        for i in range(self.chapters_list.count()):
            item = self.chapters_list.item(i)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
    
    def _select_none(self):
        """Deselect all chapters."""
        for i in range(self.chapters_list.count()):
            item = self.chapters_list.item(i)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
    
    def _on_chapter_clicked(self, item: QListWidgetItem):
        """Toggle checkbox when clicking anywhere on the item."""
        # Block selection changed signal to prevent double-toggle
        self._handling_click = True
        try:
            if item.checkState() == Qt.CheckState.Checked:
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                item.setCheckState(Qt.CheckState.Checked)
            # Clear selection after click
            self.chapters_list.clearSelection()
        finally:
            self._handling_click = False
    
    def _on_selection_changed(self):
        """Check all selected items when selection changes (for drag selection)."""
        # Skip if we're handling a click (to prevent double-toggle)
        if getattr(self, '_handling_click', False):
            return
        
        selected_items = self.chapters_list.selectedItems()
        if len(selected_items) > 1:  # Only for multi-selection (drag)
            for item in selected_items:
                item.setCheckState(Qt.CheckState.Checked)
            # Clear selection after checking
            self.chapters_list.clearSelection()
    
    def _on_download(self):
        """Handle download button click."""
        selected_chapters = []
        for i in range(self.chapters_list.count()):
            item = self.chapters_list.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                chapter = item.data(Qt.ItemDataRole.UserRole)
                if chapter:
                    selected_chapters.append(chapter)
        
        if selected_chapters:
            self.download_requested.emit(selected_chapters)
    
    def clear(self):
        """Clear all manga data."""
        self.manga_info = None
        self.chapters = []
        self.chapters_list.clear()
        self.title_label.setText("Loading manga info...")
        self.authors_label.setText("")
        self.status_label.setText("")
        self.genres_label.setText("")
        self.views_label.setText("")
        self.cover_label.setPixmap(QPixmap())
        self.cover_label.setText("Loading...")
        self.chapters_header.setText("Chapters")
