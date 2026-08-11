import os
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QScreen
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal

class CaptureOverlay(QWidget):
    selection_made = pyqtSignal(str) # returns target path
    selection_cancelled = pyqtSignal()

    def __init__(self, target_path, parent=None):
        super().__init__(parent)
        self.target_path = target_path
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Grab full screen pixmap
        screen = QApplication.primaryScreen()
        if screen:
            self.full_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.geometry())
        else:
            self.full_pixmap = QPixmap()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw background image
        if not self.full_pixmap.isNull():
            painter.drawPixmap(0, 0, self.full_pixmap)

        # Draw dark translucent overlay
        painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # If selecting, highlight selected rectangle
        if self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()
            
            # Clear selected area from dark mask
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.drawRect(rect)

            # Draw original clear screen region
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            if not self.full_pixmap.isNull():
                painter.drawPixmap(rect, self.full_pixmap, rect)

            # Draw blue border and dimensions label
            pen = QPen(QColor("#38bdf8"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            # Draw dimensions tooltip
            dim_str = f"{rect.width()} × {rect.height()} px"
            painter.setPen(QColor("#ffffff"))
            painter.setBrush(QBrush(QColor("#0284c7")))
            
            tooltip_rect = QRect(rect.x(), max(10, rect.y() - 26), 110, 22)
            painter.drawRoundedRect(tooltip_rect, 4, 4)
            painter.drawText(tooltip_rect, Qt.AlignmentFlag.AlignCenter, dim_str)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.is_selecting = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancel()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.current_pos = event.pos()
            rect = QRect(self.start_pos, self.current_pos).normalized()
            self.hide()

            if rect.width() > 10 and rect.height() > 10 and not self.full_pixmap.isNull():
                cropped = self.full_pixmap.copy(rect)
                os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
                cropped.save(self.target_path, "PNG")
                self.selection_made.emit(self.target_path)
            else:
                self.selection_cancelled.emit()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel()

    def cancel(self):
        self.hide()
        self.selection_cancelled.emit()
        self.close()
