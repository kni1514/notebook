import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath


class MonochromeKLogo(QWidget):
    def __init__(self, size=120, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_brush = QBrush(QColor(18, 18, 18))
        painter.setBrush(bg_brush)
        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.drawRoundedRect(4, 4, self.width() - 8, self.height() - 8, 20, 20)

        path = QPainterPath()
        path.addRect(34, 30, 14, 60)
        path.moveTo(48, 62)
        path.lineTo(76, 30)
        path.lineTo(92, 30)
        path.lineTo(58, 68)
        path.closeSubpath()
        path.moveTo(54, 64)
        path.lineTo(94, 90)
        path.lineTo(76, 90)
        path.lineTo(44, 70)
        path.closeSubpath()

        painter.setBrush(QBrush(QColor(220, 220, 220)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)


class WatermarkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000; color: #888888;")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)

        center_card = QWidget()
        center_card.setMaximumWidth(420)
        card_layout = QVBoxLayout(center_card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(16)

        logo = MonochromeKLogo(size=120)
        card_layout.addWidget(logo, alignment=Qt.AlignCenter)

        title_label = QLabel("notebook")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("color: #dddddd; margin-top: 4px;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #1a1a1a; max-width: 300px;")
        card_layout.addWidget(line, alignment=Qt.AlignCenter)

        mod_key = "Cmd" if sys.platform == "darwin" else "Ctrl"

        shortcuts_widget = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_widget)
        shortcuts_layout.setSpacing(10)
        shortcuts_layout.setContentsMargins(10, 8, 10, 0)

        shortcuts = [
            ("New File", f"{mod_key} + N"),
            ("Open File", f"{mod_key} + O"),
            ("Save File", f"{mod_key} + S"),
            ("Toggle Terminal", f"{mod_key} + `"),
        ]

        for label_text, key_text in shortcuts:
            row = QHBoxLayout()
            row.setContentsMargins(10, 0, 10, 0)

            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #888888;")
            row.addWidget(lbl)

            row.addStretch()

            key_badge = QLabel(key_text)
            key_badge.setFont(QFont("Consolas", 9))
            key_badge.setStyleSheet("""
                QLabel {
                    background-color: #0d0d0d;
                    color: #cccccc;
                    border: 1px solid #282828;
                    border-radius: 3px;
                    padding: 2px 7px;
                }
            """)
            row.addWidget(key_badge)

            shortcuts_layout.addLayout(row)

        card_layout.addWidget(shortcuts_widget)

        main_layout.addWidget(center_card)
