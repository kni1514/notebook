import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QIcon
from editor_widget import EditorWidget
from terminal_widget import TerminalWidget


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("notebook")
        self.resize(1100, 750)
        self.setStyleSheet("background-color: #000000;")

        # Set window icon (top left of OS window titlebar)
        icon_path = get_resource_path(os.path.join("assets", "k_icon.jpg"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setStyleSheet("""
            QSplitter {
                background-color: #000000;
            }
            QSplitter::handle {
                background-color: #141414;
                height: 2px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
        """)

        self.editor_widget = EditorWidget()
        self.splitter.addWidget(self.editor_widget)

        self.terminal_widget = TerminalWidget()
        self.splitter.addWidget(self.terminal_widget)

        self.splitter.setSizes([560, 190])

        central_layout.addWidget(self.splitter)

        mod_key = "Cmd" if sys.platform == "darwin" else "Ctrl"

        QShortcut(QKeySequence(f"{mod_key}+N"), self, lambda: self.editor_widget.new_tab())
        QShortcut(QKeySequence(f"{mod_key}+O"), self, lambda: self.editor_widget.open_file())
        QShortcut(QKeySequence(f"{mod_key}+S"), self, lambda: self.editor_widget.save_file())
        QShortcut(QKeySequence(f"{mod_key}+`"), self, self.toggle_terminal)

    def toggle_terminal(self):
        visible = self.terminal_widget.isVisible()
        if not visible:
            self.terminal_widget.start_shell()
            self.terminal_widget.show()
        else:
            self.terminal_widget.hide()


