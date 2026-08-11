import os
import sys
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QLabel, QPushButton
)
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont, QTextCursor, QKeyEvent, QTextCharFormat, QColor

ANSI_COLOR_MAP = {
    '30': QColor('#1e1e1e'),
    '31': QColor('#f44747'),
    '32': QColor('#89d185'),
    '33': QColor('#e5c07b'),
    '34': QColor('#61afef'),
    '35': QColor('#c678dd'),
    '36': QColor('#56b6c2'),
    '37': QColor('#d4d4d4'),
    '90': QColor('#666666'),
    '91': QColor('#f44747'),
    '92': QColor('#00ff9d'),
    '93': QColor('#e5c07b'),
    '94': QColor('#007acc'),
    '95': QColor('#c678dd'),
    '96': QColor('#56b6c2'),
    '97': QColor('#ffffff'),
}


class TerminalEdit(QPlainTextEdit):
    def __init__(self, process, parent=None):
        super().__init__(parent)
        self.process = process
        self.prompt_pos = 0

        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #cccccc;
                border: none;
                padding: 8px;
                selection-background-color: #264f78;
                line-height: 1.3;
            }
        """)

        self.history = []
        self.history_idx = -1

    def append_formatted_prompt(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        cwd = os.getcwd()

        fmt_cyan = QTextCharFormat()
        fmt_cyan.setForeground(QColor('#007acc'))
        fmt_cyan.setFontWeight(QFont.Bold)
        cursor.insertText("╭─ K ─ ", fmt_cyan)

        fmt_gold = QTextCharFormat()
        fmt_gold.setForeground(QColor('#e5c07b'))
        cursor.insertText(f"{cwd}\n", fmt_gold)

        fmt_green = QTextCharFormat()
        fmt_green.setForeground(QColor('#00ff9d'))
        fmt_green.setFontWeight(QFont.Bold)
        cursor.insertText("╰─❯ ", fmt_green)

        fmt_default = QTextCharFormat()
        fmt_default.setForeground(QColor('#ffffff'))
        cursor.setCharFormat(fmt_default)

        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.End)
        self.prompt_pos = self.textCursor().position()

    def append_process_output(self, text):
        if not text:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        current_full = self.toPlainText()
        if current_full.endswith("╰─❯ "):
            idx = current_full.rfind("╭─ K ─")
            if idx != -1:
                cursor.setPosition(idx, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()

        cursor.movePosition(QTextCursor.End)

        tokens = re.split(r'(\x1b\[[0-9;]*m|\r\n|\r|\n)', text)
        current_fmt = QTextCharFormat()
        current_fmt.setForeground(QColor('#cccccc'))

        for token in tokens:
            if not token:
                continue
            if token.startswith('\x1b['):
                codes = token[2:-1].split(';')
                for code in codes:
                    if code in ('0', ''):
                        current_fmt = QTextCharFormat()
                        current_fmt.setForeground(QColor('#cccccc'))
                    elif code in ANSI_COLOR_MAP:
                        current_fmt.setForeground(ANSI_COLOR_MAP[code])
            elif token in ('\r\n', '\r', '\n'):
                cursor.insertText('\n', current_fmt)
            else:
                cursor.insertText(token, current_fmt)

        if not text.endswith('\n') and not text.endswith('\r'):
            cursor.insertText('\n')

        self.setTextCursor(cursor)
        self.append_formatted_prompt()

    def keyPressEvent(self, event: QKeyEvent):
        cursor = self.textCursor()

        if cursor.position() < self.prompt_pos:
            self.moveCursor(QTextCursor.End)
            cursor = self.textCursor()

        key = event.key()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            full_text = self.toPlainText()
            cmd = full_text[self.prompt_pos:].strip()

            self.moveCursor(QTextCursor.End)
            cursor.insertText("\n")

            if cmd:
                self.history.append(cmd)
                self.history_idx = len(self.history)

                if cmd in ("clear", "cls"):
                    self.clear()
                    self.append_formatted_prompt()
                    return

                self.process.write((cmd + "\n").encode('utf-8'))
            else:
                self.append_formatted_prompt()

        elif key == Qt.Key_Backspace:
            if cursor.position() > self.prompt_pos:
                super().keyPressEvent(event)

        elif key == Qt.Key_Up:
            if self.history and self.history_idx > 0:
                self.history_idx -= 1
                self._replace_input_line(self.history[self.history_idx])

        elif key == Qt.Key_Down:
            if self.history:
                if self.history_idx < len(self.history) - 1:
                    self.history_idx += 1
                    self._replace_input_line(self.history[self.history_idx])
                else:
                    self.history_idx = len(self.history)
                    self._replace_input_line("")

        elif key == Qt.Key_Left:
            if cursor.position() > self.prompt_pos:
                super().keyPressEvent(event)

        elif key == Qt.Key_Home:
            cursor.setPosition(self.prompt_pos)
            self.setTextCursor(cursor)

        else:
            super().keyPressEvent(event)

    def _replace_input_line(self, text):
        cursor = self.textCursor()
        cursor.setPosition(self.prompt_pos, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor('#ffffff'))
        cursor.insertText(text, fmt)
        self.setTextCursor(cursor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.textCursor().position() < self.prompt_pos:
            self.moveCursor(QTextCursor.End)


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000; color: #cccccc;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: #080808; border-top: 1px solid #1a1a1a; border-bottom: 1px solid #1a1a1a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 3, 10, 3)

        title = QLabel("TERMINAL")
        title.setStyleSheet("font-weight: bold; color: #007acc; font-family: 'Segoe UI'; font-size: 11px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setToolTip("Close Terminal (Ctrl+`)")
        btn_close.clicked.connect(self.hide)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                font-size: 12px;
                font-weight: bold;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: #ffffff;
                border-radius: 2px;
            }
        """)
        header_layout.addWidget(btn_close)

        self.layout.addWidget(header)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_shell_finished)

        self.terminal_edit = TerminalEdit(process=self.process, parent=self)
        self.layout.addWidget(self.terminal_edit)

        self.start_shell()

    def start_shell(self):
        if self.process.state() == QProcess.Running:
            return

        if sys.platform == 'win32':
            shell = "powershell.exe"
            args = ["-NoLogo"]
        elif sys.platform == 'darwin':
            shell = os.environ.get('SHELL', '/bin/zsh')
            args = []
        else:
            shell = os.environ.get('SHELL', '/bin/bash')
            args = []

        try:
            self.process.start(shell, args)
            self.terminal_edit.clear()
            self.terminal_edit.append_formatted_prompt()
        except Exception as e:
            self.terminal_edit.append_process_output(f"Failed to start terminal: {str(e)}\n")

    def _on_shell_finished(self, exit_code=0, exit_status=None):
        self.hide()

    def _read_output(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace')
        self.terminal_edit.append_process_output(text)

    def send_command(self, cmd):
        if self.process.state() != QProcess.Running:
            self.start_shell()
        self.process.write((cmd + "\n").encode('utf-8'))
