import os
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QMessageBox, QApplication, QSplitter,
    QWidget
)
from PyQt6.QtGui import QPixmap, QImage, QTransform, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QPointF

from database import DatabaseManager
from icons import IconGenerator

class ImageGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene().addItem(self.pixmap_item)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: #0b0f19; border: none;")

        self._zoom = 0

    def set_image(self, filepath):
        if not os.path.exists(filepath):
            return
        pix = QPixmap(filepath)
        self.pixmap_item.setPixmap(pix)
        self.scene().setSceneRect(0, 0, pix.width(), pix.height())
        self.fit_to_screen()

    def fit_to_screen(self):
        self.resetTransform()
        self._zoom = 0
        if not self.pixmap_item.pixmap().isNull():
            self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def actual_size(self):
        self.resetTransform()
        self._zoom = 0

    def zoom_in(self):
        self.scale(1.2, 1.2)
        self._zoom += 1

    def zoom_out(self):
        self.scale(1 / 1.2, 1 / 1.2)
        self._zoom -= 1

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()


class FullViewerDialog(QDialog):
    note_updated = pyqtSignal(int, str)
    item_deleted = pyqtSignal(int)

    def __init__(self, screenshot_id: int, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.screenshot_id = screenshot_id
        self.db = db
        self.item_data = self.db.get_by_id(screenshot_id)

        self.setWindowTitle("Screenshot Viewer")
        
        # Adapt to primary screen geometry
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.resize(min(1240, geo.width()), min(680, geo.height()))
        else:
            self.resize(980, 640)

        self.all_items = self.db.get_all(sort_by="newest")
        self.current_index = 0
        for i, item in enumerate(self.all_items):
            if item["id"] == self.screenshot_id:
                self.current_index = i
                break

        self.init_ui()
        self.load_item_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("headerBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)

        self.title_label = QLabel("Screenshot Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #38bdf8;")
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()

        # Nav buttons
        self.btn_prev = QPushButton("◄ Prev")
        self.btn_prev.clicked.connect(self.navigate_prev)
        self.btn_next = QPushButton("Next ►")
        self.btn_next.clicked.connect(self.navigate_next)

        top_layout.addWidget(self.btn_prev)
        top_layout.addWidget(self.btn_next)

        # Close button
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(34, 34)
        btn_close.setStyleSheet("font-size: 16px; font-weight: bold;")
        btn_close.clicked.connect(self.accept)
        top_layout.addWidget(btn_close)

        main_layout.addWidget(top_bar)

        # Splitter: Left Image Canvas, Right Details/Notes Panel
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Image view area
        image_container = QWidget()
        img_layout = QVBoxLayout(image_container)
        img_layout.setContentsMargins(0, 0, 0, 0)

        self.graphics_view = ImageGraphicsView()
        img_layout.addWidget(self.graphics_view)

        # Zoom controls bar
        zoom_bar = QHBoxLayout()
        zoom_bar.setContentsMargins(10, 6, 10, 6)
        zoom_bar.setSpacing(8)

        btn_fit = QPushButton("🔍 Fit Screen")
        btn_fit.clicked.connect(self.graphics_view.fit_to_screen)

        btn_100 = QPushButton("100% Actual")
        btn_100.clicked.connect(self.graphics_view.actual_size)

        btn_zi = QPushButton("Zoom +")
        btn_zi.clicked.connect(self.graphics_view.zoom_in)

        btn_zo = QPushButton("Zoom -")
        btn_zo.clicked.connect(self.graphics_view.zoom_out)

        zoom_bar.addWidget(btn_fit)
        zoom_bar.addWidget(btn_100)
        zoom_bar.addWidget(btn_zi)
        zoom_bar.addWidget(btn_zo)
        zoom_bar.addStretch()

        img_layout.addLayout(zoom_bar)
        splitter.addWidget(image_container)

        # Right Panel
        panel = QFrame()
        panel.setMaximumWidth(320)
        panel.setMinimumWidth(240)
        panel.setStyleSheet("background-color: #1e293b; border-left: 1px solid #334155;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(10)

        # Metadata Header
        meta_title = QLabel("Information")
        meta_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        panel_layout.addWidget(meta_title)

        self.info_filename = QLabel()
        self.info_filename.setWordWrap(True)
        self.info_filename.setStyleSheet("font-weight: bold; color: #38bdf8; font-size: 14px;")

        self.info_dims = QLabel()
        self.info_dims.setStyleSheet("color: #94a3b8; font-size: 13px;")

        self.info_size = QLabel()
        self.info_size.setStyleSheet("color: #94a3b8; font-size: 13px;")

        self.info_date = QLabel()
        self.info_date.setStyleSheet("color: #94a3b8; font-size: 13px;")

        self.info_path = QLabel()
        self.info_path.setWordWrap(True)
        self.info_path.setStyleSheet("color: #64748b; font-size: 12px;")

        panel_layout.addWidget(self.info_filename)
        panel_layout.addWidget(self.info_dims)
        panel_layout.addWidget(self.info_size)
        panel_layout.addWidget(self.info_date)
        panel_layout.addWidget(self.info_path)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #334155;")
        panel_layout.addWidget(divider)

        # Note Section
        note_hdr = QLabel("📝 Notes")
        note_hdr.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        panel_layout.addWidget(note_hdr)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Write notes or details about this screenshot...")
        self.note_edit.setStyleSheet("min-height: 100px; font-size: 14px;")
        panel_layout.addWidget(self.note_edit)

        self.btn_save_note = QPushButton("Save Note")
        self.btn_save_note.setObjectName("btnSuccess")
        self.btn_save_note.setIcon(IconGenerator.create_note_icon(16, color="#ffffff"))
        self.btn_save_note.clicked.connect(self.save_note)
        panel_layout.addWidget(self.btn_save_note)

        panel_layout.addStretch()

        # Action Buttons
        actions_hdr = QLabel("Actions")
        actions_hdr.setStyleSheet("font-size: 14px; font-weight: bold; color: #94a3b8;")
        panel_layout.addWidget(actions_hdr)

        self.btn_copy = QPushButton("Copy Image")
        self.btn_copy.setIcon(IconGenerator.create_copy_icon(16))
        self.btn_copy.clicked.connect(self.copy_image)

        self.btn_open_folder = QPushButton("Open Folder")
        self.btn_open_folder.setIcon(IconGenerator.create_folder_icon(16))
        self.btn_open_folder.clicked.connect(self.open_folder)

        self.btn_open_sys = QPushButton("System Viewer")
        self.btn_open_sys.clicked.connect(self.open_system_viewer)

        self.btn_delete = QPushButton("Delete Screenshot")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.setIcon(IconGenerator.create_trash_icon(16, color="#ffffff"))
        self.btn_delete.clicked.connect(self.delete_item)

        panel_layout.addWidget(self.btn_copy)
        panel_layout.addWidget(self.btn_open_folder)
        panel_layout.addWidget(self.btn_open_sys)
        panel_layout.addWidget(self.btn_delete)

        splitter.addWidget(panel)
        splitter.setSizes([700, 280])

        main_layout.addWidget(splitter)

    def load_item_data(self):
        if not self.item_data:
            return

        filepath = self.item_data["filepath"]
        self.title_label.setText(f"Viewing: {self.item_data['filename']}")
        self.info_filename.setText(self.item_data["filename"])
        self.info_dims.setText(f"Dimensions: {self.item_data['width']} × {self.item_data['height']} px")
        
        kb = self.item_data['filesize'] / 1024.0
        self.info_size.setText(f"File Size: {kb:.1f} KB")
        self.info_date.setText(f"Captured: {self.item_data['timestamp']}")
        self.info_path.setText(f"Path: {filepath}")

        self.note_edit.setText(self.item_data.get("note", ""))

        self.graphics_view.set_image(filepath)

        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.all_items) - 1)

    def save_note(self):
        if not self.item_data:
            return
        new_note = self.note_edit.toPlainText().strip()
        self.db.update_note(self.item_data["id"], new_note)
        self.item_data["note"] = new_note
        self.note_updated.emit(self.item_data["id"], new_note)
        self.btn_save_note.setText("Saved!")
        QApplication.processEvents()

    def copy_image(self):
        if not self.item_data:
            return
        app = QApplication.instance()
        if app:
            img = QImage(self.item_data["filepath"])
            if not img.isNull():
                app.clipboard().setImage(img)
                self.btn_copy.setText("Copied!")

    def open_folder(self):
        if not self.item_data:
            return
        filepath = self.item_data["filepath"]
        if os.path.exists(filepath):
            folder = os.path.dirname(filepath)
            subprocess.Popen(["xdg-open", folder])

    def open_system_viewer(self):
        if not self.item_data:
            return
        filepath = self.item_data["filepath"]
        if os.path.exists(filepath):
            subprocess.Popen(["xdg-open", filepath])

    def delete_item(self):
        if not self.item_data:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.item_data['filename']}'?\nThis will remove the file permanently.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            item_id = self.item_data["id"]
            self.db.delete_screenshot(item_id, delete_file=True)
            self.item_deleted.emit(item_id)
            
            # Remove from local list and navigate
            self.all_items.pop(self.current_index)
            if self.all_items:
                if self.current_index >= len(self.all_items):
                    self.current_index = len(self.all_items) - 1
                self.item_data = self.all_items[self.current_index]
                self.load_item_data()
            else:
                self.accept()

    def navigate_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.item_data = self.all_items[self.current_index]
            self.load_item_data()

    def navigate_next(self):
        if self.current_index < len(self.all_items) - 1:
            self.current_index += 1
            self.item_data = self.all_items[self.current_index]
            self.load_item_data()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.navigate_prev()
        elif event.key() == Qt.Key.Key_Right:
            self.navigate_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)
