import os
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QComboBox, QGridLayout, QMessageBox,
    QApplication, QSizePolicy, QInputDialog
)
from PyQt6.QtGui import QPixmap, QImage, QCloseEvent
from PyQt6.QtCore import Qt, pyqtSignal

from config import ConfigManager
from database import DatabaseManager
from capture import CaptureEngine
from icons import IconGenerator
from ui.viewer_window import FullViewerDialog
from ui.settings_dialog import SettingsDialog

class ScreenshotCard(QFrame):
    clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    edit_note_requested = pyqtSignal(int)
    copy_requested = pyqtSignal(int)

    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.screenshot_id = item_data["id"]

        self.setObjectName("cardFrame")
        self.setFixedSize(230, 270)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Thumbnail Label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(210, 130)
        self.thumb_label.setStyleSheet("background-color: #0f172a; border-radius: 6px;")
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        thumbpath = self.item_data.get("thumbpath") or self.item_data["filepath"]
        if os.path.exists(thumbpath):
            pix = QPixmap(thumbpath)
            if not pix.isNull():
                scaled = pix.scaled(210, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.thumb_label.setPixmap(scaled)

        self.thumb_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumb_label.mousePressEvent = lambda e: self.clicked.emit(self.screenshot_id)
        layout.addWidget(self.thumb_label)

        # Info line 1: Filename + Resolution badge
        info_row1 = QHBoxLayout()
        fn = self.item_data["filename"]
        fn_truncated = fn if len(fn) <= 17 else fn[:14] + "..."
        lbl_fn = QLabel(fn_truncated)
        lbl_fn.setToolTip(fn)
        lbl_fn.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 13px;")

        w, h = self.item_data.get("width", 0), self.item_data.get("height", 0)
        lbl_res = QLabel(f"{w}×{h}")
        lbl_res.setStyleSheet("background-color: #0284c7; color: #ffffff; border-radius: 4px; padding: 2px 6px; font-size: 11px; font-weight: bold;")

        info_row1.addWidget(lbl_fn)
        info_row1.addStretch()
        info_row1.addWidget(lbl_res)
        layout.addLayout(info_row1)

        # Info line 2: Date & Size
        ts = self.item_data.get("timestamp", "")
        size_kb = self.item_data.get("filesize", 0) / 1024.0
        lbl_meta = QLabel(f"{ts} • {size_kb:.0f}KB")
        lbl_meta.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_meta)

        # Note Snippet Box
        note_text = self.item_data.get("note", "").strip()
        self.lbl_note = QLabel()
        if note_text:
            snippet = note_text if len(note_text) <= 26 else note_text[:23] + "..."
            self.lbl_note.setText(f"📝 {snippet}")
            self.lbl_note.setStyleSheet("color: #10b981; font-size: 13px; font-weight: 500;")
            self.lbl_note.setToolTip(note_text)
        else:
            self.lbl_note.setText("+ Add note...")
            self.lbl_note.setStyleSheet("color: #64748b; font-size: 12px; font-style: italic;")

        self.lbl_note.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_note.mousePressEvent = lambda e: self.edit_note_requested.emit(self.screenshot_id)
        layout.addWidget(self.lbl_note)

        # Bottom Quick Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        btn_view = QPushButton("View")
        btn_view.setStyleSheet("padding: 4px 10px; font-size: 13px;")
        btn_view.clicked.connect(lambda: self.clicked.emit(self.screenshot_id))

        btn_copy = QPushButton()
        btn_copy.setFixedSize(30, 30)
        btn_copy.setIcon(IconGenerator.create_copy_icon(16))
        btn_copy.setToolTip("Copy Image")
        btn_copy.clicked.connect(lambda: self.copy_requested.emit(self.screenshot_id))

        btn_note = QPushButton()
        btn_note.setFixedSize(30, 30)
        btn_note.setIcon(IconGenerator.create_note_icon(16))
        btn_note.setToolTip("Edit Note")
        btn_note.clicked.connect(lambda: self.edit_note_requested.emit(self.screenshot_id))

        btn_del = QPushButton()
        btn_del.setFixedSize(30, 30)
        btn_del.setObjectName("btnDanger")
        btn_del.setIcon(IconGenerator.create_trash_icon(16, color="#ffffff"))
        btn_del.setToolTip("Delete Screenshot")
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.screenshot_id))

        btn_row.addWidget(btn_view)
        btn_row.addStretch()
        btn_row.addWidget(btn_copy)
        btn_row.addWidget(btn_note)
        btn_row.addWidget(btn_del)
        layout.addLayout(btn_row)

    def mouseDoubleClickEvent(self, event):
        self.clicked.emit(self.screenshot_id)


class MainWindow(QMainWindow):
    def __init__(self, config: ConfigManager, db: DatabaseManager, capture_engine: CaptureEngine):
        super().__init__()
        self.config = config
        self.db = db
        self.capture_engine = capture_engine

        self.setWindowTitle("SnapNotes — Screen Capture & History")
        
        # Optimize for 1280x720 display
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.resize(min(1240, geo.width()), min(680, geo.height()))
        else:
            self.resize(960, 640)

        self.setMinimumSize(600, 400)

        self.init_ui()
        self.refresh_gallery()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Bar Container
        header = QFrame()
        header.setObjectName("headerBar")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)

        # Row 1: App Title + Capture Modes (Area, Focus App, App Window, Full, Delay)
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        logo_lbl = QLabel()
        logo_lbl.setPixmap(IconGenerator.create_camera_icon(32, color="#38bdf8", bg="transparent").pixmap(32, 32))
        row1.addWidget(logo_lbl)

        title = QLabel("SnapNotes")
        title.setObjectName("appNameLabel")
        row1.addWidget(title)

        row1.addSpacing(6)

        btn_cap_area = QPushButton("📸 Area")
        btn_cap_area.setObjectName("btnPrimary")
        btn_cap_area.setToolTip("Capture selected area of screen")
        btn_cap_area.clicked.connect(self.trigger_capture_area)
        row1.addWidget(btn_cap_area)

        btn_cap_focus = QPushButton("🎯 Focus App")
        btn_cap_focus.setToolTip("Click target application to bring to front, then snip area")
        btn_cap_focus.clicked.connect(self.trigger_capture_focus_app)
        row1.addWidget(btn_cap_focus)

        btn_cap_win = QPushButton("🪟 App Window")
        btn_cap_win.setToolTip("Click any application window to capture it directly")
        btn_cap_win.clicked.connect(self.trigger_capture_window)
        row1.addWidget(btn_cap_win)

        btn_cap_full = QPushButton("🖥️ Full")
        btn_cap_full.setToolTip("Capture full screen")
        btn_cap_full.clicked.connect(self.trigger_capture_fullscreen)
        row1.addWidget(btn_cap_full)

        btn_cap_delay = QPushButton("⏱️ 3s")
        btn_cap_delay.setToolTip("Capture after 3 second delay")
        btn_cap_delay.clicked.connect(self.trigger_capture_delayed)
        row1.addWidget(btn_cap_delay)

        row1.addStretch()

        self.lbl_stats = QLabel("0 Screenshots")
        self.lbl_stats.setObjectName("statsLabel")
        row1.addWidget(self.lbl_stats)

        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.clicked.connect(self.open_settings)
        row1.addWidget(btn_settings)

        header_layout.addLayout(row1)

        # Row 2: Search Input + Folder Button + Sort Selector
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Search notes or filenames...")
        self.txt_search.setMinimumWidth(220)
        self.txt_search.textChanged.connect(self.refresh_gallery)
        row2.addWidget(self.txt_search)

        btn_open_dir = QPushButton("📁 Save Folder")
        btn_open_dir.setIcon(IconGenerator.create_folder_icon(16))
        btn_open_dir.clicked.connect(self.open_save_folder)
        row2.addWidget(btn_open_dir)

        row2.addStretch()

        lbl_sort = QLabel("Sort:")
        lbl_sort.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")
        row2.addWidget(lbl_sort)

        self.combo_sort = QComboBox()
        self.combo_sort.addItems(["Newest First", "Oldest First", "Largest Size", "Smallest Size"])
        self.combo_sort.currentIndexChanged.connect(self.refresh_gallery)
        row2.addWidget(self.combo_sort)

        header_layout.addLayout(row2)
        main_layout.addWidget(header)

        # Gallery Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.gallery_container = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_container)
        self.gallery_layout.setContentsMargins(14, 14, 14, 14)
        self.gallery_layout.setSpacing(14)
        self.gallery_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.gallery_container)
        main_layout.addWidget(self.scroll_area)

    def refresh_gallery(self):
        # Sync folder first
        self.db.sync_directory(self.config.save_directory)

        # Clear existing layout
        for i in reversed(range(self.gallery_layout.count())):
            widget = self.gallery_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        search_q = self.txt_search.text().strip()
        sort_mode = self.combo_sort.currentText()
        sort_key = "newest"
        if sort_mode == "Oldest First":
            sort_key = "oldest"
        elif sort_mode == "Largest Size":
            sort_key = "largest"
        elif sort_mode == "Smallest Size":
            sort_key = "smallest"

        items = self.db.get_all(search_query=search_q, sort_by=sort_key)

        # Update stats
        total_items = len(items)
        total_bytes = sum(it.get("filesize", 0) for it in items)
        total_mb = total_bytes / (1024.0 * 1024.0)
        self.lbl_stats.setText(f"{total_items} Items ({total_mb:.1f} MB)")

        if not items:
            empty_lbl = QLabel("📷 No screenshots found.\nClick '📸 Area' or '🎯 Focus App' above to start!")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #64748b; font-size: 16px; margin-top: 40px;")
            self.gallery_layout.addWidget(empty_lbl, 0, 0)
            return

        # Calculate grid columns based on width
        col_count = max(1, self.width() // 250)
        for idx, item in enumerate(items):
            row = idx // col_count
            col = idx % col_count
            card = ScreenshotCard(item)
            card.clicked.connect(self.open_viewer)
            card.delete_requested.connect(self.delete_item)
            card.edit_note_requested.connect(self.edit_note)
            card.copy_requested.connect(self.copy_image)
            self.gallery_layout.addWidget(card, row, col)

    def trigger_capture_area(self):
        self.hide()
        QApplication.processEvents()
        self.capture_engine.capture_area()

    def trigger_capture_focus_app(self):
        self.hide()
        QApplication.processEvents()
        self.capture_engine.capture_focus_app(delay_seconds=3)

    def trigger_capture_window(self):
        self.hide()
        QApplication.processEvents()
        self.capture_engine.capture_window()

    def trigger_capture_fullscreen(self):
        self.hide()
        QApplication.processEvents()
        self.capture_engine.capture_fullscreen()

    def trigger_capture_delayed(self):
        self.hide()
        QApplication.processEvents()
        self.capture_engine.capture_delayed(3, mode="area")

    def open_viewer(self, screenshot_id: int):
        dlg = FullViewerDialog(screenshot_id, self.db, self)
        dlg.note_updated.connect(lambda sid, note: self.refresh_gallery())
        dlg.item_deleted.connect(lambda sid: self.refresh_gallery())
        dlg.exec()
        self.refresh_gallery()

    def edit_note(self, screenshot_id: int):
        item = self.db.get_by_id(screenshot_id)
        if not item:
            return
        curr_note = item.get("note", "")
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Edit Screenshot Note",
            f"Notes for '{item['filename']}':",
            curr_note
        )
        if ok:
            self.db.update_note(screenshot_id, text.strip())
            self.refresh_gallery()

    def copy_image(self, screenshot_id: int):
        item = self.db.get_by_id(screenshot_id)
        if item:
            self.capture_engine.copy_to_clipboard(item["filepath"])

    def delete_item(self, screenshot_id: int):
        item = self.db.get_by_id(screenshot_id)
        if not item:
            return

        reply = QMessageBox.question(
            self,
            "Delete Screenshot",
            f"Delete screenshot '{item['filename']}'?\nThis will remove the file from your computer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_screenshot(screenshot_id, delete_file=True)
            self.refresh_gallery()

    def open_save_folder(self):
        save_dir = self.config.save_directory
        if os.path.exists(save_dir):
            subprocess.Popen(["xdg-open", save_dir])

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        dlg.settings_saved.connect(self.refresh_gallery)
        dlg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_gallery()

    def closeEvent(self, event: QCloseEvent):
        if self.config.get("minimize_to_tray_on_close", True):
            event.ignore()
            self.hide()
        else:
            event.accept()
