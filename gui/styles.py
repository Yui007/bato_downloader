"""
Modern dark theme styles for PyQt6 GUI.
"""

# Color palette
COLORS = {
    'bg_primary': '#0f0f1a',
    'bg_secondary': '#1a1a2e',
    'bg_tertiary': '#252542',
    'bg_card': '#1e1e35',
    'accent_primary': '#7c3aed',
    'accent_secondary': '#a855f7',
    'accent_gradient_start': '#7c3aed',
    'accent_gradient_end': '#ec4899',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0b0',
    'text_muted': '#6b6b7b',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'border': '#3a3a5c',
}

# Main application stylesheet
MAIN_STYLESHEET = f"""
/* Global styles */
QMainWindow, QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['bg_tertiary']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['accent_primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['bg_tertiary']};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['accent_primary']};
}}

/* Line Edit */
QLineEdit {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 15px;
    color: {COLORS['text_primary']};
    font-size: 14px;
    selection-background-color: {COLORS['accent_primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_primary']};
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

/* Push Button */
QPushButton {{
    background-color: {COLORS['accent_primary']};
    color: {COLORS['text_primary']};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_secondary']};
}}

QPushButton:pressed {{
    background-color: #6d28d9;
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_muted']};
}}

/* Secondary button style */
QPushButton[class="secondary"] {{
    background-color: {COLORS['bg_tertiary']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['bg_card']};
    border-color: {COLORS['accent_primary']};
}}

/* Labels */
QLabel {{
    color: {COLORS['text_primary']};
}}

QLabel[class="title"] {{
    font-size: 24px;
    font-weight: 700;
}}

QLabel[class="subtitle"] {{
    font-size: 16px;
    color: {COLORS['text_secondary']};
}}

QLabel[class="muted"] {{
    color: {COLORS['text_muted']};
    font-size: 12px;
}}

/* List Widget */
QListWidget {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 5px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    border-radius: 6px;
    padding: 10px;
    margin: 2px 0;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_tertiary']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent_primary']};
}}

/* Checkbox */
QCheckBox {{
    spacing: 8px;
    color: {COLORS['text_primary']};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_secondary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent_primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_primary']};
    border-color: {COLORS['accent_primary']};
}}

/* Combo Box */
QComboBox {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {COLORS['text_primary']};
    min-width: 150px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent_primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_primary']};
    padding: 5px;
}}

/* Spin Box */
QSpinBox {{
    background-color: {COLORS['bg_secondary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 15px;
    color: {COLORS['text_primary']};
}}

QSpinBox:focus {{
    border-color: {COLORS['accent_primary']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 20px;
    border: none;
    background: transparent;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-size: 10px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_gradient_start']},
        stop:1 {COLORS['accent_gradient_end']});
    border-radius: 6px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: none;
    background: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 12px 20px;
    border: none;
    font-weight: 500;
}}

QTabBar::tab:hover {{
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    color: {COLORS['accent_primary']};
    border-bottom: 3px solid {COLORS['accent_primary']};
}}

/* Group Box */
QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    margin-top: 15px;
    padding: 15px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 10px;
    color: {COLORS['text_primary']};
}}

/* Tool Tip */
QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
}}
"""

# Card widget style
CARD_STYLE = f"""
QFrame {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}

QFrame:hover {{
    border-color: {COLORS['accent_primary']};
}}
"""

# Sidebar navigation style
SIDEBAR_STYLE = f"""
QFrame {{
    background-color: {COLORS['bg_secondary']};
    border-right: 1px solid {COLORS['border']};
}}

QPushButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    text-align: left;
    padding: 15px 20px;
    border-radius: 0;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QPushButton:checked {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['accent_primary']};
    border-left: 3px solid {COLORS['accent_primary']};
}}
"""

# Header style
HEADER_STYLE = f"""
QLabel {{
    font-size: 28px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}
"""
