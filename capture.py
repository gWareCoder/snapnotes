import os
import time
import datetime
import subprocess
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from config import ConfigManager
from database import DatabaseManager

class CaptureEngine(QObject):
    capture_completed = pyqtSignal(dict) # Emits screenshot metadata dict
    capture_cancelled = pyqtSignal()
    countdown_tick = pyqtSignal(int)

    def __init__(self, config: ConfigManager, db: DatabaseManager):
        super().__init__()
        self.config = config
        self.db = db
        self.banner = None

    def generate_filepath(self):
        save_dir = self.config.save_directory
        pattern = self.config.get("filename_pattern", "Screenshot_%Y-%m-%d_%H-%M-%S.png")
        now = datetime.datetime.now()
        filename = now.strftime(pattern)
        
        # Ensure extension
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filename += ".png"
            
        full_path = os.path.join(save_dir, filename)
        
        # Handle duplicate filenames
        base, ext = os.path.splitext(full_path)
        counter = 1
        while os.path.exists(full_path):
            full_path = f"{base}_{counter}{ext}"
            counter += 1
            
        return full_path

    def capture_area(self):
        """Captures a selected screen region."""
        target_path = self.generate_filepath()
        engine_type = self.config.get("capture_engine", "slurp")

        if engine_type == "slurp":
            return self._capture_area_slurp(target_path)
        else:
            return self._capture_area_overlay(target_path)

    def capture_window(self):
        """Captures a specific application window by clicking it."""
        return self.capture_area()

    def capture_focus_app(self, delay_seconds=3):
        """Shows floating banner allowing user to click & bring target application to focus before area capture."""
        from ui.focus_banner import FocusBannerWidget
        
        if self.banner:
            try:
                self.banner.close()
            except Exception:
                pass

        self.banner = FocusBannerWidget(countdown_seconds=delay_seconds)
        self.banner.snip_requested.connect(self.capture_area)
        self.banner.cancelled.connect(self.capture_cancelled.emit)
        self.banner.show()

    def _capture_area_slurp(self, target_path):
        try:
            # Run slurp to get selection rectangle or clicked window bounds
            slurp_cmd = [
                "slurp",
                "-b", "#00000080",
                "-c", "#38bdf8",
                "-s", "#38bdf820",
                "-w", "2"
            ]
            res = subprocess.run(slurp_cmd, capture_output=True, text=True)
            if res.returncode != 0 or not res.stdout.strip():
                print("[CaptureEngine] Region selection cancelled by user.")
                self.capture_cancelled.emit()
                return None

            geometry = res.stdout.strip()

            # Run grim to capture selected geometry
            grim_cmd = ["grim", "-g", geometry, target_path]
            grim_res = subprocess.run(grim_cmd, capture_output=True, text=True)
            if grim_res.returncode == 0 and os.path.exists(target_path):
                return self._on_capture_success(target_path)
            else:
                print(f"[CaptureEngine] Grim error: {grim_res.stderr}")
                self.capture_cancelled.emit()
                return None

        except Exception as e:
            print(f"[CaptureEngine] Error in slurp capture: {e}")
            self.capture_cancelled.emit()
            return None

    def _capture_area_overlay(self, target_path):
        from ui.capture_overlay import CaptureOverlay
        self.overlay = CaptureOverlay(target_path)
        self.overlay.selection_made.connect(self._on_capture_success)
        self.overlay.selection_cancelled.connect(self.capture_cancelled.emit)
        self.overlay.show()

    def capture_fullscreen(self):
        """Captures the entire active screen."""
        target_path = self.generate_filepath()
        try:
            grim_cmd = ["grim", target_path]
            res = subprocess.run(grim_cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(target_path):
                return self._on_capture_success(target_path)
            else:
                print(f"[CaptureEngine] Fullscreen grim error: {res.stderr}")
                self.capture_cancelled.emit()
                return None
        except Exception as e:
            print(f"[CaptureEngine] Error in fullscreen capture: {e}")
            self.capture_cancelled.emit()
            return None

    def capture_delayed(self, delay_seconds=3, mode="area"):
        """Captures after a delay."""
        self.remaining_seconds = delay_seconds
        self.delay_mode = mode

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(1000)
        self.countdown_tick.emit(self.remaining_seconds)

    def _on_timer_tick(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.countdown_tick.emit(self.remaining_seconds)
        else:
            self.timer.stop()
            self.countdown_tick.emit(0)
            if self.delay_mode == "area":
                self.capture_area()
            else:
                self.capture_fullscreen()

    def _on_capture_success(self, target_path, note=""):
        if not os.path.exists(target_path):
            self.capture_cancelled.emit()
            return None

        # Save to database
        item_id = self.db.add_screenshot(target_path, note=note)
        item_data = self.db.get_by_id(item_id) if item_id else None

        # Copy to clipboard if configured
        if self.config.get("copy_to_clipboard", True):
            self.copy_to_clipboard(target_path)

        if item_data:
            self.capture_completed.emit(item_data)
        return item_data

    @staticmethod
    def copy_to_clipboard(filepath):
        if not os.path.exists(filepath):
            return
        app = QApplication.instance()
        if app:
            cb = app.clipboard()
            image = QImage(filepath)
            if not image.isNull():
                cb.setImage(image)
                print(f"[CaptureEngine] Copied screenshot to clipboard: {filepath}")
