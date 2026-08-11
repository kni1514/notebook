import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QFont, QIcon
from app_window import MainWindow, get_resource_path


def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("notebook")

    icon_path = get_resource_path(os.path.join("assets", "k_icon.jpg"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.WindowText, QColor(204, 204, 204))
    dark_palette.setColor(QPalette.Base, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.AlternateBase, QColor(10, 10, 10))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.ToolTipText, QColor(204, 204, 204))
    dark_palette.setColor(QPalette.Text, QColor(204, 204, 204))
    dark_palette.setColor(QPalette.Button, QColor(15, 15, 15))
    dark_palette.setColor(QPalette.ButtonText, QColor(204, 204, 204))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(0, 122, 204))
    dark_palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

