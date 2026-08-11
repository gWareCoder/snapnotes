import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

class IconGenerator:
    _icon_cache = {}

    @classmethod
    def create_camera_icon(cls, size=64, color="#00aaff", bg="#1a202c"):
        key = f"camera_{size}_{color}_{bg}"
        if key in cls._icon_cache:
            return cls._icon_cache[key]

        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded background circle
        if bg and bg != "transparent":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(bg)))
            painter.drawEllipse(0, 0, size, size)

        # Draw Camera Body
        pen = QPen(QColor(color), size * 0.07)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        pad = size * 0.22
        cw = size - 2 * pad
        ch = cw * 0.72
        cx = pad
        cy = pad + (size - 2 * pad - ch) / 2 + size * 0.05

        # Top lens bump
        top_w = cw * 0.35
        top_h = ch * 0.2
        top_x = cx + (cw - top_w) / 2
        top_y = cy - top_h + 1
        path = QPainterPath()
        path.addRoundedRect(QRectF(top_x, top_y, top_w, top_h), 3, 3)
        painter.drawPath(path)

        # Main box
        path_box = QPainterPath()
        path_box.addRoundedRect(QRectF(cx, cy, cw, ch), 8, 8)
        painter.drawPath(path_box)

        # Lens circle
        lens_r = ch * 0.32
        lens_cx = cx + cw / 2
        lens_cy = cy + ch / 2
        painter.drawEllipse(QPointF(lens_cx, lens_cy), lens_r, lens_r)

        # Lens dot/flash
        flash_r = size * 0.04
        painter.setBrush(QBrush(QColor(color)))
        painter.drawEllipse(QPointF(cx + cw * 0.78, cy + ch * 0.28), flash_r, flash_r)

        painter.end()

        icon = QIcon(pix)
        cls._icon_cache[key] = icon
        return icon

    @classmethod
    def create_tray_icon(cls, size=32):
        return cls.create_camera_icon(size=size, color="#38bdf8", bg="#0f172a")

    @classmethod
    def create_folder_icon(cls, size=32, color="#f59e0b"):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(color), 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(color).lighter(160)))

        path = QPainterPath()
        path.moveTo(4, 8)
        path.lineTo(12, 8)
        path.lineTo(15, 11)
        path.lineTo(size - 4, 11)
        path.lineTo(size - 4, size - 6)
        path.lineTo(4, size - 6)
        path.closeSubpath()
        painter.drawPath(path)
        painter.end()
        return QIcon(pix)

    @classmethod
    def create_note_icon(cls, size=32, color="#10b981"):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(color), 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(color).lighter(170)))

        rect = QRectF(6, 4, size - 12, size - 8)
        painter.drawRoundedRect(rect, 4, 4)

        # Draw lines inside note
        painter.setPen(QPen(QColor(color), 1.5))
        painter.drawLine(10, 10, size - 10, 10)
        painter.drawLine(10, 15, size - 10, 15)
        painter.drawLine(10, 20, size - 14, 20)

        painter.end()
        return QIcon(pix)

    @classmethod
    def create_trash_icon(cls, size=32, color="#ef4444"):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(color), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Lid
        painter.drawLine(6, 9, size - 6, 9)
        painter.drawLine(12, 6, size - 12, 6)

        # Can body
        path = QPainterPath()
        path.moveTo(8, 10)
        path.lineTo(10, size - 4)
        path.lineTo(size - 10, size - 4)
        path.lineTo(size - 8, 10)
        painter.drawPath(path)

        # Inner vertical lines
        painter.drawLine(13, 13, 13, size - 7)
        painter.drawLine(size - 13, 13, size - 13, size - 7)

        painter.end()
        return QIcon(pix)

    @classmethod
    def create_copy_icon(cls, size=32, color="#a855f7"):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(color), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Back card
        painter.drawRoundedRect(QRectF(10, 4, size - 14, size - 12), 3, 3)
        # Front card
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.drawRoundedRect(QRectF(4, 10, size - 14, size - 12), 3, 3)

        painter.end()
        return QIcon(pix)
