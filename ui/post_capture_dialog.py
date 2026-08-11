import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QApplication, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal

from icons import IconGenerator

class PostCaptureDialog(QDialog):
    note_saved = pyqtSignal(int, str)
    discard_requested = pyqtSignal(int)
    open_viewer_requested = pyqtSignal(int)

    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.screenshot_id = item_data["id"]
        self.filepath = item_data["filepath"]
        self.thumbpath = item_data.get("thumbpath") or self.filepath

        self.setWindowTitle("Screenshot Captured")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Container card
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)

        # Header with title and close X button
        header = QHBoxLayout()
        title_label = QLabel("📸 Screenshot Captured!")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #38bdf8;")
        header.addWidget(title_label)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 16px; color: #94a3b8; font-weight: bold;")
        close_btn.clicked.connect(self.accept)
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # Content horizontal layout: Thumbnail preview + Metadata info
        body = QHBoxLayout()
        body.setSpacing(12)
        
        # Thumbnail label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(140, 100)
        self.thumb_label.setStyleSheet("background-color: #0f172a; border-radius: 6px; border: 1px solid #334155;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_thumbnail()
        body.addWidget(self.thumb_label)

        # Details
        info_layout = QVBoxLayout()
        fn_label = QLabel(os.path.basename(self.filepath))
        fn_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #ffffff;")
        fn_label.setWordWrap(True)

        w, h = self.item_data.get("width", 0), self.item_data.get("height", 0)
        size_kb = self.item_data.get("filesize", 0) / 1024.0
        meta_label = QLabel(f"Dimensions: {w} × {h} px\nSize: {size_kb:.1f} KB")
        meta_label.setStyleSheet("font-size: 12px; color: #94a3b8;")

        info_layout.addWidget(fn_label)
        info_layout.addWidget(meta_label)
        info_layout.addStretch()
        body.addLayout(info_layout)

        card_layout.addLayout(body)

        # Note Input
        note_hdr = QLabel("📝 Add Note / Description:")
        note_hdr.setStyleSheet("font-size: 13px; color: #38bdf8; font-weight: bold;")
        card_layout.addWidget(note_hdr)

        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Type a note about this screenshot...")
        self.note_edit.setStyleSheet("font-size: 15px; padding: 8px 12px;")
        self.note_edit.setText(self.item_data.get("note", ""))
        self.note_edit.returnPressed.connect(self.on_save_note)
        card_layout.addWidget(self.note_edit)

        # Actions buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setIcon(IconGenerator.create_copy_icon(16))
        self.btn_copy.clicked.connect(self.on_copy)

        self.btn_view = QPushButton("View")
        self.btn_view.clicked.connect(self.on_view)

        self.btn_save = QPushButton("Save Note")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.setIcon(IconGenerator.create_note_icon(16, color="#ffffff"))
        self.btn_save.clicked.connect(self.on_save_note)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setIcon(IconGenerator.create_trash_icon(16, color="#ffffff"))
        self.btn_delete.clicked.connect(self.on_discard)

        btn_row.addWidget(self.btn_copy)
        btn_row.addWidget(self.btn_view)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)

        card_layout.addLayout(btn_row)
        main_layout.addWidget(card)

        # Position at bottom-right of primary screen
        self.position_on_screen()

    def load_thumbnail(self):
        pix = QPixmap(self.thumbpath)
        if not pix.isNull():
            scaled = pix.scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.thumb_label.setPixmap(scaled)

    def position_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            req_size = self.sizeHint()
            x = geo.right() - req_size.width() - 20
            y = geo.bottom() - req_size.height() - 40
            self.move(max(10, x), max(10, y))

    def on_save_note(self):
        note_text = self.note_edit.text().strip()
        self.note_saved.emit(self.screenshot_id, note_text)
        self.accept()

    def on_copy(self):
        app = QApplication.instance()
        if app:
            img = QImage(self.filepath)
            if not img.isNull():
                app.clipboard().setImage(img)
                self.btn_copy.setText("Copied!")

    def on_view(self):
        self.open_viewer_requested.emit(self.screenshot_id)
        self.accept()

    def on_discard(self):
        self.discard_requested.emit(self.screenshot_id)
        self.reject()
