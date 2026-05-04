import sys
import os
import json

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal

from db import init_db
from api import Api


def get_frontend_path():
    """
    Returns the URL to index.html.
    Works both during development and when packaged as .exe via PyInstaller.
    """
    if getattr(sys, "_MEIPASS", None):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "frontend", "index.html")
    return QUrl.fromLocalFile(path)


class Bridge(QObject):
    """
    Exposes Python Api methods to JavaScript via QWebChannel.
    JS calls window.bridge.call(method, args) and gets result back via callback.
    """

    # Signal to send result back to JS
    result_ready = pyqtSignal(str, str)  # (call_id, json_result)

    def __init__(self, api):
        super().__init__()
        self.api = api

    @pyqtSlot(str, str, str)
    def call(self, call_id, method, args_json):
        """
        Called from JS as: bridge.call(call_id, method_name, json_args)
        Looks up the method on Api, calls it, returns JSON result.
        """
        try:
            args = json.loads(args_json) if args_json else []
            fn = getattr(self.api, method, None)
            if fn is None:
                result = {"ok": False, "error": f"Method '{method}' not found"}
            else:
                result = fn(*args)
        except Exception as e:
            result = {"ok": False, "error": str(e)}

        self.result_ready.emit(call_id, json.dumps(result))


class MainWindow(QMainWindow):
    def __init__(self, bridge):
        super().__init__()
        self.setWindowTitle("Budgeteer")
        self.setMinimumSize(1200, 600)

        # Web view
        self.view = QWebEngineView()

        self.view.page().setDevToolsPage(None)

        # Set up web channel (Python ↔ JS bridge)
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", bridge)
        self.view.page().setWebChannel(self.channel)

        # Connect result signal → send back to JS
        bridge.result_ready.connect(self._send_result)

        # Load frontend
        self.view.load(get_frontend_path())
        self.setCentralWidget(self.view)

    def _send_result(self, call_id, json_result):
        """Sends the Python result back to the waiting JS callback."""
        safe = json_result.replace("\\", "\\\\").replace("`", "\\`")
        js = f"window.__resolveCall(`{call_id}`, `{safe}`)"
        self.view.page().runJavaScript(js)


if __name__ == "__main__":
    # Init database
    init_db()

    # Create app
    app = QApplication(sys.argv)
    app.setApplicationName("Budgeteer")

    # Create bridge and window
    api    = Api()
    bridge = Bridge(api)
    window = MainWindow(bridge)
    window.showMaximized()

    sys.exit(app.exec())
