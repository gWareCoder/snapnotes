DARK_STYLE = """
/* SnapNotes Modern Dark Theme QSS */

QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #0f172a;
}

/* Header & Controls Bar */
#headerBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 8px 12px;
}

#appNameLabel {
    font-size: 18px;
    font-weight: bold;
    color: #38bdf8;
}

#statsLabel {
    color: #94a3b8;
    font-size: 12px;
}

/* Push Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton#btnPrimary {
    background-color: #0284c7;
    color: #ffffff;
    border: none;
    font-weight: bold;
}

QPushButton#btnPrimary:hover {
    background-color: #0369a1;
}

QPushButton#btnDanger {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
}

QPushButton#btnDanger:hover {
    background-color: #b91c1c;
}

QPushButton#btnSuccess {
    background-color: #059669;
    color: #ffffff;
    border: none;
}

QPushButton#btnSuccess:hover {
    background-color: #047857;
}

/* Line Edit & Text Edit */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #0284c7;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #38bdf8;
}

/* Combo Box */
QComboBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #0284c7;
    border: 1px solid #334155;
}

/* Scroll Area & Scroll Bar */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background-color: #0f172a;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Cards & Frames */
QFrame#cardFrame {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

QFrame#cardFrame:hover {
    border: 1px solid #38bdf8;
    background-color: #24334a;
}

/* Tooltips */
QToolTip {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 4px;
    padding: 4px 8px;
}

/* Checkboxes */
QCheckBox {
    color: #f8fafc;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #334155;
    background-color: #1e293b;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

/* Status Bar */
QStatusBar {
    background-color: #0f172a;
    color: #94a3b8;
    border-top: 1px solid #334155;
}
"""
