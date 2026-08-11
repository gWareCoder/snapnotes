from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

class FocusBannerWidget(QWidget):
    snip_requested = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, countdown_seconds=3, parent=None):
        super().__init__(parent)
        self.remaining_seconds = countdown_seconds

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumWidth(460)

        self.init_ui()

        # Timer countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(1000)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #0284c7;
                border: 2px solid #38bdf8;
                border-radius: 10px;
                padding: 6px 14px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1e293b;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 13pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f172a;
            }
        """)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 6, 10, 6)
        card_layout.setSpacing(12)

        self.lbl_status = QLabel(f"Click target app to focus... ({self.remaining_seconds}s)")
        card_layout.addWidget(self.lbl_status)

        btn_snip = QPushButton("Snip Now")
        btn_snip.clicked.connect(self.trigger_snip)
        card_layout.addWidget(btn_snip)

        btn_more = QPushButton("+2s")
        btn_more.setToolTip("Add 2 seconds to focus target application")
        btn_more.clicked.connect(self.add_time)
        card_layout.addWidget(btn_more)

        btn_cancel = QPushButton("✕")
        btn_cancel.setFixedSize(30, 30)
        btn_cancel.clicked.connect(self.cancel)
        card_layout.addWidget(btn_cancel)

        layout.addWidget(card)

        self.position_top_center()

    def position_top_center(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            req_size = self.sizeHint()
            x = geo.left() + (geo.width() - req_size.width()) // 2
            y = geo.top() + 15
            self.move(max(10, x), y)

    def on_timer_tick(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.lbl_status.setText(f"Click target app to focus... ({self.remaining_seconds}s)")
        else:
            self.timer.stop()
            self.trigger_snip()

    def add_time(self):
        self.remaining_seconds += 2
        self.lbl_status.setText(f"Click target app to focus... ({self.remaining_seconds}s)")

    def trigger_snip(self):
        self.timer.stop()
        self.hide()
        self.snip_requested.emit()
        self.close()

    def cancel(self):
        self.timer.stop()
        self.hide()
        self.cancelled.emit()
        self.close()
