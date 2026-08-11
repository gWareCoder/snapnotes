import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QFrame, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from config import ConfigManager
from icons import IconGenerator

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config

        self.setWindowTitle("SnapNotes Settings")
        self.setMinimumWidth(500)
        self.resize(540, 420)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Storage Location Group
        group_storage = QGroupBox("Screenshot Storage Location")
        group_storage.setStyleSheet("QGroupBox { font-weight: bold; color: #38bdf8; margin-top: 10px; font-size: 14pt; } QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        storage_layout = QVBoxLayout(group_storage)
        storage_layout.setSpacing(8)

        lbl_desc = QLabel("Screenshots will be saved automatically to this folder:")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 13pt;")
        storage_layout.addWidget(lbl_desc)

        path_row = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setText(self.config.save_directory)
        path_row.addWidget(self.txt_path)

        btn_browse = QPushButton("Browse...")
        btn_browse.setIcon(IconGenerator.create_folder_icon(18))
        btn_browse.clicked.connect(self.browse_folder)
        path_row.addWidget(btn_browse)

        storage_layout.addLayout(path_row)
        main_layout.addWidget(group_storage)

        # Capture Behavior Group
        group_behavior = QGroupBox("Capture Options & Behavior")
        group_behavior.setStyleSheet("QGroupBox { font-weight: bold; color: #38bdf8; margin-top: 10px; font-size: 14pt; } QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        beh_layout = QVBoxLayout(group_behavior)
        beh_layout.setSpacing(10)

        self.chk_prompt_note = QCheckBox("Show 'Add Note' popup immediately after taking screenshot")
        self.chk_prompt_note.setChecked(self.config.get("prompt_note_after_capture", True))
        beh_layout.addWidget(self.chk_prompt_note)

        self.chk_auto_copy = QCheckBox("Automatically copy new screenshots to Clipboard")
        self.chk_auto_copy.setChecked(self.config.get("copy_to_clipboard", True))
        beh_layout.addWidget(self.chk_auto_copy)

        self.chk_minimize_tray = QCheckBox("Closing history window minimizes application to System Tray")
        self.chk_minimize_tray.setChecked(self.config.get("minimize_to_tray_on_close", True))
        beh_layout.addWidget(self.chk_minimize_tray)

        self.chk_start_tray = QCheckBox("Start application minimized in System Tray")
        self.chk_start_tray.setChecked(self.config.get("start_in_tray", False))
        beh_layout.addWidget(self.chk_start_tray)

        main_layout.addWidget(group_behavior)

        # Quick Hotkey info
        group_hotkey = QGroupBox("Global Shortcut / Hotkey Tip")
        group_hotkey.setStyleSheet("QGroupBox { font-weight: bold; color: #38bdf8; margin-top: 10px; font-size: 14pt; } QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        hk_layout = QVBoxLayout(group_hotkey)
        lbl_hk = QLabel("You can bind system shortcut keys (e.g., Ctrl+Shift+S or PrintScreen) in your OS settings to launch:\n  python3 /home/tomg/snapnotes/main.py --capture")
        lbl_hk.setStyleSheet("color: #94a3b8; font-size: 12pt;")
        hk_layout.addWidget(lbl_hk)
        main_layout.addWidget(group_hotkey)

        main_layout.addStretch()

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("btnPrimary")
        btn_save.clicked.connect(self.save_settings)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        main_layout.addLayout(btn_row)

    def browse_folder(self):
        current_dir = self.txt_path.text().strip() or os.path.expanduser("~/Pictures/Screenshots")
        chosen = QFileDialog.getExistingDirectory(self, "Select Screenshot Save Folder", current_dir)
        if chosen:
            self.txt_path.setText(chosen)

    def save_settings(self):
        chosen_dir = self.txt_path.text().strip()
        if not chosen_dir:
            QMessageBox.warning(self, "Invalid Path", "Please specify a valid storage path.")
            return

        try:
            os.makedirs(chosen_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error Creating Directory", f"Failed to create directory:\n{e}")
            return

        self.config.save_directory = chosen_dir
        self.config.set("prompt_note_after_capture", self.chk_prompt_note.isChecked())
        self.config.set("copy_to_clipboard", self.chk_auto_copy.isChecked())
        self.config.set("minimize_to_tray_on_close", self.chk_minimize_tray.isChecked())
        self.config.set("start_in_tray", self.chk_start_tray.isChecked())

        self.settings_saved.emit()
        self.accept()
