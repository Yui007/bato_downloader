"""
Download progress widget.
"""

from typing import Optional, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QListWidget, QListWidgetItem,
    QFrame, QScrollArea
)

from gui.styles import COLORS


class DownloadItemWidget(QFrame):
    """Widget representing a single chapter download."""
    
    def __init__(self, chapter_number: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.chapter_number = chapter_number
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Header row
        header_layout = QHBoxLayout()
        
        # Chapter name
        self.name_label = QLabel(f"Chapter {self.chapter_number}")
        self.name_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Pending")
        self.status_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m images")
        layout.addWidget(self.progress_bar)
    
    def set_total(self, total: int):
        """Set total images count."""
        self.progress_bar.setMaximum(total)
        self.status_label.setText("Downloading...")
        self.status_label.setStyleSheet(f"color: {COLORS['accent_primary']};")
    
    def set_progress(self, downloaded: int, total: int):
        """Update progress."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(downloaded)
    
    def set_completed(self, success: bool):
        """Mark download as completed."""
        if success:
            self.status_label.setText("✓ Completed")
            self.status_label.setStyleSheet(f"color: {COLORS['success']};")
            self.progress_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {COLORS['success']};
                }}
            """)
        else:
            self.status_label.setText("✗ Failed")
            self.status_label.setStyleSheet(f"color: {COLORS['error']};")
            self.progress_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {COLORS['error']};
                }}
            """)


class DownloadWidget(QWidget):
    """Download queue and progress screen."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.download_items: Dict[str, DownloadItemWidget] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("⬇️ Downloads")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel All")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.setEnabled(False)
        header_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(header_layout)
        
        # Overall progress
        self.overall_frame = QFrame()
        self.overall_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        overall_layout = QVBoxLayout(self.overall_frame)
        
        self.overall_label = QLabel("No active downloads")
        self.overall_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text_secondary']};
        """)
        overall_layout.addWidget(self.overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setMinimumHeight(20)
        overall_layout.addWidget(self.overall_progress)
        
        layout.addWidget(self.overall_frame)
        
        # Downloads list container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, 1)
        
        # Empty state
        self.empty_label = QLabel("Select chapters from a manga to start downloading")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text_muted']};
            padding: 50px;
        """)
        layout.addWidget(self.empty_label)
    
    def start_downloads(self, chapters: list, manga_title: str):
        """Initialize download UI for chapters."""
        self.clear()
        self.empty_label.hide()
        self.cancel_btn.setEnabled(True)
        
        self.overall_label.setText(f"Downloading {len(chapters)} chapters from {manga_title}")
        self.overall_progress.setMaximum(len(chapters))
        self.overall_progress.setValue(0)
        
        for chapter in chapters:
            item_widget = DownloadItemWidget(chapter.number)
            self.download_items[chapter.number] = item_widget
            
            # Insert before the stretch
            self.scroll_layout.insertWidget(
                self.scroll_layout.count() - 1,
                item_widget
            )
    
    def on_chapter_started(self, chapter_number: str, total_images: int):
        """Handle chapter download started."""
        if chapter_number in self.download_items:
            self.download_items[chapter_number].set_total(total_images)
    
    def on_chapter_progress(self, chapter_number: str, downloaded: int, total: int):
        """Handle chapter progress update."""
        if chapter_number in self.download_items:
            self.download_items[chapter_number].set_progress(downloaded, total)
    
    def on_chapter_completed(self, chapter_number: str, success: bool):
        """Handle chapter download completed."""
        if chapter_number in self.download_items:
            self.download_items[chapter_number].set_completed(success)
        
        # Update overall progress
        completed = sum(
            1 for item in self.download_items.values()
            if "Completed" in item.status_label.text() or "Failed" in item.status_label.text()
        )
        self.overall_progress.setValue(completed)
    
    def on_all_completed(self):
        """Handle all downloads completed."""
        self.cancel_btn.setEnabled(False)
        self.overall_label.setText("All downloads completed!")
        self.overall_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['success']};
        """)
    
    def clear(self):
        """Clear all download items."""
        for item in self.download_items.values():
            item.deleteLater()
        self.download_items.clear()
        self.empty_label.show()
        self.overall_progress.setValue(0)
        self.overall_label.setText("No active downloads")
        self.overall_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text_secondary']};
        """)
