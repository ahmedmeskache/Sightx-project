import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.login import LoginWindow
from ui.welcome import WelcomeWindow
from ui.dashboard import DashboardWindow
from ui.history import HistoryWindow


class SightXApp:
    def __init__(self):
        self.login_window = None
        self.welcome_window = None
        self.dashboard_window = None
        self.history_window = None

    def start(self):
        self.login_window = LoginWindow()
        self.login_window.sig_success.connect(self.open_welcome)
        self.login_window.show()

    def open_welcome(self):
        if self.login_window:
            self.login_window.close()
            self.login_window = None

        self.welcome_window = WelcomeWindow()
        self.welcome_window.sig_camera.connect(self.open_camera)
        self.welcome_window.sig_history.connect(self.open_history)
        self.welcome_window.show()

    def open_camera(self):
        self.welcome_window.hide()
        self.dashboard_window = DashboardWindow()
        self.dashboard_window.sig_back.connect(self.back_from_camera)
        self.dashboard_window.show()

    def back_from_camera(self):
        if self.dashboard_window:
            self.dashboard_window.close()
            self.dashboard_window = None
        self.welcome_window.show()

    def open_history(self):
        self.welcome_window.hide()
        log = self.dashboard_window.alert_log if self.dashboard_window else None
        self.history_window = HistoryWindow(alert_log=log)
        self.history_window.sig_back.connect(self.back_from_history)
        self.history_window.show()

    def back_from_history(self):
        if self.history_window:
            self.history_window.close()
            self.history_window = None
        self.welcome_window.show()


if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    qt_app.setFont(QFont("Segoe UI", 10))
    app_instance = SightXApp()
    app_instance.start()
    sys.exit(qt_app.exec_())