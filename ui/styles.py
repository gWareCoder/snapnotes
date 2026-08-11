DARK_STYLE = """
/* SnapNotes Modern Dark Theme — 14pt Font & Handheld Optimized */

QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
    font-size: 14pt;
}

QMainWindow, QDialog {
    background-color: #0f172a;
}

/* Header & Controls Bar */
#headerBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 10px 14px;
}

#appNameLabel {
    font-size: 20pt;
    font-weight: bold;
    color: #38bdf8;
}

#statsLabel {
    color: #94a3b8;
    font-size: 12pt;
}

/* Push Buttons — 14pt Large Click Targets */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14pt;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #38bdf8;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton#btnPrimary {
    background-color: #0284c7;
    color: #ffffff;
    border: none;
    font-size: 14pt;
    font-weight: bold;
    padding: 9px 18px;
}

QPushButton#btnPrimary:hover {
    background-color: #0369a1;
}

QPushButton#btnDanger {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
    font-size: 14pt;
    font-weight: bold;
}

QPushButton#btnDanger:hover {
    background-color: #b91c1c;
}

QPushButton#btnSuccess {
    background-color: #059669;
    color: #ffffff;
    border: none;
    font-size: 14pt;
    font-weight: bold;
}

QPushButton#btnSuccess:hover {
    background-color: #047857;
}

/* Line Edit & Text Edit — 14pt High Contrast */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e293b;
    color: #ffffff;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14pt;
    selection-background-color: #0284c7;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #38bdf8;
}

/* Combo Box */
QComboBox {
    background-color: #1e293b;
    color: #ffffff;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14pt;
    font-weight: 500;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left-width: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #ffffff;
    selection-background-color: #0284c7;
    border: 1px solid #334155;
    font-size: 14pt;
}

/* Scroll Area & Scroll Bar — Touch / Trackball Friendly */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background-color: #0f172a;
    width: 16px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 35px;
    border-radius: 8px;
}

QScrollBar::handle:vertical:hover {
    background-color: #38bdf8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Cards & Frames */
QFrame#cardFrame {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}

QFrame#cardFrame:hover {
    border: 2px solid #38bdf8;
    background-color: #24334a;
}

/* Tooltips */
QToolTip {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13pt;
}

/* Checkboxes */
QCheckBox {
    color: #f8fafc;
    spacing: 10px;
    font-size: 14pt;
}

QCheckBox::indicator {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: 1px solid #334155;
    background-color: #1e293b;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}
"""
