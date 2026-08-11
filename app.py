import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, Qt

from config import ConfigManager
from database import DatabaseManager
from capture import CaptureEngine
from icons import IconGenerator
from ui.main_window import MainWindow
from ui.post_capture_dialog import PostCaptureDialog
from ui.viewer_window import FullViewerDialog
from ui.styles import DARK_STYLE

class SnapNotesApp(QObject):
    def __init__(self, argv):
        super().__init__()
        # Force XCB platform if Wayland plugin missing
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        
        self.qapp = QApplication(argv)
        self.qapp.setStyleSheet(DARK_STYLE)
        self.qapp.setQuitOnLastWindowClosed(False)

        self.config = ConfigManager()
        self.db = DatabaseManager()
        self.capture_engine = CaptureEngine(self.config, self.db)

        self.main_window = MainWindow(self.config, self.db, self.capture_engine)

        self.setup_tray()
        self.connect_signals()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(IconGenerator.create_tray_icon(32))
        self.tray_icon.setToolTip("SnapNotes — Screen Capture & History")

        # Tray Context Menu
        menu = QMenu()
        menu.setStyleSheet(DARK_STYLE)

        act_area = QAction(IconGenerator.create_camera_icon(18, color="#38bdf8", bg="transparent"), "📸 Capture Area", self)
        act_area.triggered.connect(self.on_capture_area)

        act_full = QAction("🖥️ Capture Fullscreen", self)
        act_full.triggered.connect(self.on_capture_fullscreen)

        act_delay = QAction("⏱️ Capture Delayed (3s)", self)
        act_delay.triggered.connect(self.on_capture_delayed)

        act_gallery = QAction("🖼️ Open Gallery & History", self)
        act_gallery.triggered.connect(self.show_main_window)

        act_folder = QAction(IconGenerator.create_folder_icon(18), "📁 Open Save Folder", self)
        act_folder.triggered.connect(self.on_open_folder)

        act_settings = QAction("⚙️ Settings", self)
        act_settings.triggered.connect(self.main_window.open_settings)

        act_quit = QAction("❌ Quit SnapNotes", self)
        act_quit.triggered.connect(self.quit_app)

        menu.addAction(act_area)
        menu.addAction(act_full)
        menu.addAction(act_delay)
        menu.addSeparator()
        menu.addAction(act_gallery)
        menu.addAction(act_folder)
        menu.addAction(act_settings)
        menu.addSeparator()
        menu.addAction(act_quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def connect_signals(self):
        self.capture_engine.capture_completed.connect(self.on_capture_completed)
        self.capture_engine.capture_cancelled.connect(self.on_capture_cancelled)

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_main_window()

    def toggle_main_window(self):
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.show_main_window()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def on_capture_area(self):
        self.main_window.hide()
        self.capture_engine.capture_area()

    def on_capture_fullscreen(self):
        self.main_window.hide()
        self.capture_engine.capture_fullscreen()

    def on_capture_delayed(self):
        self.main_window.hide()
        self.capture_engine.capture_delayed(3, mode="area")

    def on_capture_completed(self, item_data: dict):
        # Refresh main window gallery
        self.main_window.refresh_gallery()

        # Show notification in tray
        self.tray_icon.showMessage(
            "Screenshot Captured",
            f"Saved: {item_data['filename']}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

        # Check if post-capture note prompt enabled
        if self.config.get("prompt_note_after_capture", True):
            dlg = PostCaptureDialog(item_data)
            dlg.note_saved.connect(self.on_note_saved)
            dlg.discard_requested.connect(self.on_item_discarded)
            dlg.open_viewer_requested.connect(self.on_open_viewer)
            dlg.exec()

    def on_capture_cancelled(self):
        # If cancelled, restore main window if it was visible before
        pass

    def on_note_saved(self, screenshot_id: int, note_text: str):
        self.db.update_note(screenshot_id, note_text)
        self.main_window.refresh_gallery()

    def on_item_discarded(self, screenshot_id: int):
        self.db.delete_screenshot(screenshot_id, delete_file=True)
        self.main_window.refresh_gallery()

    def on_open_viewer(self, screenshot_id: int):
        self.show_main_window()
        self.main_window.open_viewer(screenshot_id)

    def on_open_folder(self):
        folder = self.config.save_directory
        if os.path.exists(folder):
            subprocess.Popen(["xdg-open", folder])

    def quit_app(self):
        self.tray_icon.hide()
        self.qapp.quit()

    def run(self, start_in_tray=False):
        if not start_in_tray:
            self.show_main_window()
        return self.qapp.exec()
