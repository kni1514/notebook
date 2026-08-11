import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFileDialog, QMessageBox, QStackedWidget
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from editor_html import MONACO_EDITOR_HTML
from watermark_widget import WatermarkWidget


EXTENSION_LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.json': 'json',
    '.md': 'markdown',
    '.cpp': 'cpp',
    '.c': 'cpp',
    '.h': 'cpp',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.java': 'java',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
    '.ps1': 'powershell',
    '.bat': 'bat',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.ini': 'ini'
}


class EditorTab(QWidget):
    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        self.web_view.setHtml(MONACO_EDITOR_HTML, QUrl("http://localhost"))
        self.web_view.loadFinished.connect(self._on_editor_loaded)
        self.pending_content = ""
        self.pending_language = "python"

    def set_file(self, file_path, content):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower() if file_path else ""
        lang = EXTENSION_LANGUAGE_MAP.get(ext, 'plaintext')
        self.set_content(content, lang)

    def set_content(self, content, language='python'):
        self.pending_content = content
        self.pending_language = language
        escaped_content = (
            content.replace('\\', '\\\\')
            .replace('`', '\\`')
            .replace('$', '\\$')
        )
        js_code = f"monacoSetContent(`{escaped_content}`); monacoSetLanguage('{language}');"
        self.web_view.page().runJavaScript(js_code)

    def _on_editor_loaded(self, ok):
        if ok and self.pending_content:
            self.set_content(self.pending_content, self.pending_language)

    def get_content(self, callback):
        self.web_view.page().runJavaScript("monacoGetContent();", callback)


class EditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.watermark = WatermarkWidget()
        self.stack.addWidget(self.watermark)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.stack.addWidget(self.tabs)

        self.setStyleSheet("background-color: #000000;")
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #000000;
            }
            QTabBar {
                background-color: #050505;
                border-bottom: 1px solid #1a1a1a;
            }
            QTabBar::tab {
                background-color: #0d0d0d;
                color: #aaaaaa;
                padding: 7px 24px 7px 14px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                border: 1px solid #1a1a1a;
            }
            QTabBar::tab:selected {
                background-color: #000000;
                color: #ffffff;
                border-top: 2px solid #007acc;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #141414;
                color: #dddddd;
            }
            QTabBar::close-button {
                subcontrol-position: right;
                subcontrol-origin: padding;
                margin-right: 4px;
                padding: 2px;
            }
            QTabBar::close-button:hover {
                background-color: #222222;
                border-radius: 2px;
            }
        """)

        self.stack.setCurrentWidget(self.watermark)

    def _show_tabs_if_hidden(self):
        if self.stack.currentWidget() != self.tabs:
            self.stack.setCurrentWidget(self.tabs)

    def new_tab(self, title="Untitled", content=""):
        self._show_tabs_if_hidden()
        tab = EditorTab()
        index = self.tabs.addTab(tab, title)
        self.tabs.setCurrentIndex(index)
        if content:
            tab.set_content(content)
        return tab

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                self._show_tabs_if_hidden()

                for i in range(self.tabs.count()):
                    tab = self.tabs.widget(i)
                    if tab.file_path == file_path:
                        self.tabs.setCurrentIndex(i)
                        return

                title = os.path.basename(file_path)
                tab = EditorTab(file_path=file_path)
                index = self.tabs.addTab(tab, title)
                self.tabs.setCurrentIndex(index)
                tab.set_file(file_path, content)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        if self.stack.currentWidget() != self.tabs:
            return

        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return

        if current_tab.file_path:
            self._save_to_path(current_tab, current_tab.file_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        if self.stack.currentWidget() != self.tabs:
            return

        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "All Files (*);;Python Files (*.py);;JavaScript Files (*.js)"
        )
        if file_path:
            self._save_to_path(current_tab, file_path)

    def _save_to_path(self, tab, file_path):
        def on_content_retrieved(content):
            try:
                dir_name = os.path.dirname(file_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                save_text = content if content is not None else tab.pending_content

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(save_text)

                tab.file_path = file_path
                tab.pending_content = save_text

                index = self.tabs.indexOf(tab)
                if index != -1:
                    self.tabs.setTabText(index, os.path.basename(file_path))

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{str(e)}")

        tab.get_content(on_content_retrieved)

    def close_tab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.stack.setCurrentWidget(self.watermark)
