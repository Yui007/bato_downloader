"""
Settings widget for configuration.
"""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QFrame, QLineEdit, QFileDialog
)

from src.config import get_config, save_config, CONFIG_DIR
from gui.styles import COLORS


class SettingsWidget(QWidget):
    """Settings configuration screen."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("⚙️ Settings")
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(header)
        
        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(15)
        
        # Download format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Images Only", "PDF", "CBZ (Comic Book Archive)"])
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        download_layout.addRow("Download Format:", self.format_combo)
        
        # Keep images checkbox
        self.keep_images_cb = QCheckBox("Keep original images after conversion")
        self.keep_images_cb.stateChanged.connect(self._on_setting_changed)
        download_layout.addRow("", self.keep_images_cb)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Default: Project folder")
        self.output_dir_input.textChanged.connect(self._on_setting_changed)
        output_dir_layout.addWidget(self.output_dir_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(self.browse_btn)
        
        download_layout.addRow("Output Directory:", output_dir_layout)
        
        layout.addWidget(download_group)
        
        # Concurrency Settings Group
        concurrency_group = QGroupBox("Concurrent Downloads")
        concurrency_layout = QFormLayout(concurrency_group)
        concurrency_layout.setSpacing(15)
        
        # Concurrent chapters
        self.concurrent_chapters_spin = QSpinBox()
        self.concurrent_chapters_spin.setRange(1, 10)
        self.concurrent_chapters_spin.valueChanged.connect(self._on_setting_changed)
        concurrency_layout.addRow("Simultaneous Chapters:", self.concurrent_chapters_spin)
        
        # Concurrent images
        self.concurrent_images_spin = QSpinBox()
        self.concurrent_images_spin.setRange(1, 20)
        self.concurrent_images_spin.valueChanged.connect(self._on_setting_changed)
        concurrency_layout.addRow("Simultaneous Images per Chapter:", self.concurrent_images_spin)
        
        # Description
        desc_label = QLabel(
            "Higher values = faster downloads, but may cause rate limiting.\n"
            "Recommended: 3 chapters, 5 images."
        )
        desc_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        desc_label.setWordWrap(True)
        concurrency_layout.addRow("", desc_label)
        
        layout.addWidget(concurrency_group)
        
        # Retry Settings Group
        retry_group = QGroupBox("Retry Settings")
        retry_layout = QFormLayout(retry_group)
        retry_layout.setSpacing(15)
        
        # Max chapter retries
        self.chapter_retries_spin = QSpinBox()
        self.chapter_retries_spin.setRange(0, 10)
        self.chapter_retries_spin.valueChanged.connect(self._on_setting_changed)
        retry_layout.addRow("Max Chapter Retries:", self.chapter_retries_spin)
        
        # Max image retries
        self.image_retries_spin = QSpinBox()
        self.image_retries_spin.setRange(0, 10)
        self.image_retries_spin.valueChanged.connect(self._on_setting_changed)
        retry_layout.addRow("Max Image Retries:", self.image_retries_spin)
        
        layout.addWidget(retry_group)
        
        # Logging Settings Group
        logging_group = QGroupBox("Logging")
        logging_layout = QVBoxLayout(logging_group)
        logging_layout.setSpacing(10)
        
        self.enable_logs_cb = QCheckBox("Enable detailed logs (for debugging)")
        self.enable_logs_cb.stateChanged.connect(self._on_logging_changed)
        logging_layout.addWidget(self.enable_logs_cb)
        
        log_desc = QLabel(
            "When enabled, detailed download progress will be shown in console."
        )
        log_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        logging_layout.addWidget(log_desc)
        
        layout.addWidget(logging_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Save button
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(self.save_btn)
        
        buttons_layout.addStretch()
        
        # Save status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {COLORS['success']};")
        buttons_layout.addWidget(self.status_label)
        
        layout.addLayout(buttons_layout)
    
    def _load_settings(self):
        """Load current settings into UI."""
        config = get_config()
        
        # Block signals to prevent triggering _on_setting_changed during load
        self.format_combo.blockSignals(True)
        self.keep_images_cb.blockSignals(True)
        self.output_dir_input.blockSignals(True)
        self.concurrent_chapters_spin.blockSignals(True)
        self.concurrent_images_spin.blockSignals(True)
        self.chapter_retries_spin.blockSignals(True)
        self.image_retries_spin.blockSignals(True)
        self.enable_logs_cb.blockSignals(True)
        
        try:
            # Download format
            format_index = {"images": 0, "pdf": 1, "cbz": 2}
            self.format_combo.setCurrentIndex(format_index.get(config.download_format, 0))
            
            # Keep images
            self.keep_images_cb.setChecked(config.keep_images_after_conversion)
            self._update_keep_images_state()
            
            # Output directory
            self.output_dir_input.setText(config.output_directory)
            
            # Concurrency
            self.concurrent_chapters_spin.setValue(config.concurrent_chapters)
            self.concurrent_images_spin.setValue(config.concurrent_images)
            
            # Retries
            self.chapter_retries_spin.setValue(config.max_chapter_retries)
            self.image_retries_spin.setValue(config.max_image_retries)
            
            # Logging
            self.enable_logs_cb.setChecked(config.enable_detailed_logs)
        finally:
            # Unblock signals
            self.format_combo.blockSignals(False)
            self.keep_images_cb.blockSignals(False)
            self.output_dir_input.blockSignals(False)
            self.concurrent_chapters_spin.blockSignals(False)
            self.concurrent_images_spin.blockSignals(False)
            self.chapter_retries_spin.blockSignals(False)
            self.image_retries_spin.blockSignals(False)
            self.enable_logs_cb.blockSignals(False)
        
        # Clear any stale status
        self.status_label.setText("")
    
    def _on_format_changed(self, index: int):
        """Handle format dropdown change."""
        self._update_keep_images_state()
        self._on_setting_changed()
    
    def _update_keep_images_state(self):
        """Enable/disable keep images based on format."""
        # Only relevant for PDF/CBZ
        format_index = self.format_combo.currentIndex()
        self.keep_images_cb.setEnabled(format_index > 0)
    
    def _on_setting_changed(self):
        """Save settings when changed."""
        config = get_config()
        
        # Download format
        format_map = {0: "images", 1: "pdf", 2: "cbz"}
        config.download_format = format_map.get(self.format_combo.currentIndex(), "images")
        
        # Keep images
        config.keep_images_after_conversion = self.keep_images_cb.isChecked()
        
        # Output directory
        config.output_directory = self.output_dir_input.text().strip()
        
        # Concurrency
        config.concurrent_chapters = self.concurrent_chapters_spin.value()
        config.concurrent_images = self.concurrent_images_spin.value()
        
        # Retries
        config.max_chapter_retries = self.chapter_retries_spin.value()
        config.max_image_retries = self.image_retries_spin.value()
        
        save_config()
        self._show_saved()
        self.settings_changed.emit()
    
    def _on_logging_changed(self, state: int):
        """Handle logging checkbox change."""
        config = get_config()
        config.enable_detailed_logs = state == Qt.CheckState.Checked.value
        save_config()
        
        # Update logger
        from src.logger import setup_logger
        setup_logger(config.enable_detailed_logs)
        
        self._show_saved()
    
    def _show_saved(self):
        """Show saved indicator briefly."""
        self.status_label.setText("✓ Settings saved")
        # Could add a timer to clear this after a few seconds
    
    def _save_settings(self):
        """Explicit save button handler."""
        self._on_setting_changed()
        self.status_label.setText("✓ Settings saved successfully!")
    
    def _browse_output_dir(self):
        """Open folder browser for output directory."""
        current = self.output_dir_input.text().strip()
        if not current:
            current = str(CONFIG_DIR)
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current
        )
        if folder:
            self.output_dir_input.setText(folder)

