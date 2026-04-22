import sys
import os
import logging
import ctypes

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from ui.main_window import MainWindow

_ROOT = os.path.dirname(os.path.abspath(__file__))

# 🔥 FIX TASKBAR ICON (VERY IMPORTANT)
myappid = "zipzap.app.v1"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def main():
    app = QApplication(sys.argv)

    icon_path = os.path.join(_ROOT, "zipzap.ico")

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setApplicationName("ZipZap")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()

    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()