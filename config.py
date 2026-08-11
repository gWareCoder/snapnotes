import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/snapnotes")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_SAVE_DIR = os.path.expanduser("~/Pictures/Screenshots")

DEFAULT_CONFIG = {
    "save_directory": DEFAULT_SAVE_DIR,
    "filename_pattern": "Screenshot_%Y-%m-%d_%H-%M-%S.png",
    "prompt_note_after_capture": True,
    "copy_to_clipboard": True,
    "minimize_to_tray_on_close": True,
    "start_in_tray": False,
    "thumbnail_size": 280,
    "capture_engine": "slurp"  # 'slurp' or 'overlay'
}

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"[ConfigManager] Error loading config: {e}")
        else:
            self.save()

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    @property
    def save_directory(self):
        save_dir = os.path.expanduser(self.data.get("save_directory", DEFAULT_SAVE_DIR))
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    @save_directory.setter
    def save_directory(self, path):
        expanded = os.path.expanduser(path)
        os.makedirs(expanded, exist_ok=True)
        self.data["save_directory"] = expanded
        self.save()
