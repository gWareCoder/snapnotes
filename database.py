import os
import sqlite3
import datetime
from PIL import Image

DB_DIR = os.path.expanduser("~/.config/snapnotes")
DB_FILE = os.path.join(DB_DIR, "snapnotes.db")
THUMB_DIR = os.path.expanduser("~/.cache/snapnotes/thumbnails")

class DatabaseManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        os.makedirs(DB_DIR, exist_ok=True)
        os.makedirs(THUMB_DIR, exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    thumbpath TEXT,
                    timestamp DATETIME NOT NULL,
                    width INTEGER DEFAULT 0,
                    height INTEGER DEFAULT 0,
                    filesize INTEGER DEFAULT 0,
                    note TEXT DEFAULT ''
                )
            """)
            conn.commit()

    def generate_thumbnail(self, filepath, size=(300, 300)):
        if not os.path.exists(filepath):
            return ""
        try:
            import hashlib
            filename = os.path.basename(filepath)
            path_hash = hashlib.md5(filepath.encode('utf-8')).hexdigest()[:12]
            thumb_filename = f"thumb_{path_hash}_{filename}"
            if not thumb_filename.lower().endswith((".png", ".jpg", ".jpeg")):
                thumb_filename += ".png"
            thumb_path = os.path.join(THUMB_DIR, thumb_filename)
            
            if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
                return thumb_path

            with Image.open(filepath) as img:
                img.thumbnail(size)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(thumb_path, format="PNG")
            return thumb_path
        except Exception as e:
            print(f"[DatabaseManager] Failed to generate thumbnail for {filepath}: {e}")
            return ""

    def add_screenshot(self, filepath, note=""):
        if not os.path.exists(filepath):
            return None

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        width, height = 0, 0
        try:
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            pass

        thumbpath = self.generate_thumbnail(filepath)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO screenshots (filepath, filename, thumbpath, timestamp, width, height, filesize, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(filepath) DO UPDATE SET
                    thumbpath=excluded.thumbpath,
                    width=excluded.width,
                    height=excluded.height,
                    filesize=excluded.filesize
            """, (filepath, filename, thumbpath, now_str, width, height, filesize, note))
            conn.commit()
            return cursor.lastrowid

    def update_note(self, screenshot_id, note):
        with self.get_connection() as conn:
            conn.execute("UPDATE screenshots SET note = ? WHERE id = ?", (note, screenshot_id))
            conn.commit()

    def delete_screenshot(self, screenshot_id, delete_file=True):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, thumbpath FROM screenshots WHERE id = ?", (screenshot_id,))
            row = cursor.fetchone()
            if row:
                filepath = row["filepath"]
                thumbpath = row["thumbpath"]
                
                cursor.execute("DELETE FROM screenshots WHERE id = ?", (screenshot_id,))
                conn.commit()

                if delete_file:
                    if filepath and os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print(f"[DatabaseManager] Failed to delete file {filepath}: {e}")
                    if thumbpath and os.path.exists(thumbpath):
                        try:
                            os.remove(thumbpath)
                        except Exception as e:
                            print(f"[DatabaseManager] Failed to delete thumbnail {thumbpath}: {e}")
                return True
        return False

    def get_all(self, search_query="", sort_by="newest"):
        query = "SELECT * FROM screenshots"
        params = []

        if search_query.strip():
            query += " WHERE note LIKE ? OR filename LIKE ? OR timestamp LIKE ?"
            pattern = f"%{search_query.strip()}%"
            params.extend([pattern, pattern, pattern])

        if sort_by == "oldest":
            query += " ORDER BY id ASC"
        elif sort_by == "largest":
            query += " ORDER BY filesize DESC"
        elif sort_by == "smallest":
            query += " ORDER BY filesize ASC"
        else: # newest
            query += " ORDER BY id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_by_id(self, screenshot_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM screenshots WHERE id = ?", (screenshot_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def sync_directory(self, save_dir):
        if not os.path.exists(save_dir):
            return
        
        valid_exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        
        # 1. Clean records for missing files
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filepath, thumbpath FROM screenshots")
            rows = cursor.fetchall()
            for r in rows:
                if not os.path.exists(r["filepath"]):
                    cursor.execute("DELETE FROM screenshots WHERE id = ?", (r["id"],))
                    if r["thumbpath"] and os.path.exists(r["thumbpath"]):
                        try:
                            os.remove(r["thumbpath"])
                        except Exception:
                            pass
            conn.commit()

        # 2. Add new files from save_dir
        for f in os.listdir(save_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                full_path = os.path.join(save_dir, f)
                if os.path.isfile(full_path):
                    with self.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id, thumbpath FROM screenshots WHERE filepath = ?", (full_path,))
                        row = cursor.fetchone()
                        if not row:
                            self.add_screenshot(full_path)
                        elif not row["thumbpath"] or not os.path.exists(row["thumbpath"]):
                            new_thumb = self.generate_thumbnail(full_path)
                            cursor.execute("UPDATE screenshots SET thumbpath = ? WHERE id = ?", (new_thumb, row["id"]))
                            conn.commit()
