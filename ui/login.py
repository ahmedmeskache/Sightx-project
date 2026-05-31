import sys, os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

BACKGROUND_COLOR = "#09090b"
PANEL_COLOR = "#0f0f12"
CARD_COLOR = "#141418"
INPUT_COLOR = "#1a1a20"
ACCENT_COLOR = "#c8ff00"
TEXT_COLOR = "#ffffff"
SECONDARY_TEXT_COLOR = "#888899"
MUTED_TEXT_COLOR = "#333344"
BORDER_COLOR = "#1c1c24"
ERROR_COLOR = "#ff3344"

CREDENTIALS = {
    "EMP-001": "SX2026",
    "EMP-002": "ALPHA1",
    "EMP-003": "BETA99",
}


class LoginWindow(QMainWindow):
    sig_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SightX — Authentication")
        self.setMinimumSize(1280, 760)
        self.setStyleSheet(f"background: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        self._build_interface()

    def _build_interface(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addStretch(1)

        card_frame = QFrame()
        card_frame.setFixedWidth(420)
        card_frame.setStyleSheet(f"""
            QFrame {{
                background: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 16px;
            }}
        """)

        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(18)

        title_label = QLabel("SIGHTX")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"color: {ACCENT_COLOR}; font-size: 32px; font-weight: 900; "
            f"letter-spacing: 6px; font-family: 'Courier New';")
        card_layout.addWidget(title_label)

        subtitle_label = QLabel("Security System Access")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(
            f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px; "
            f"letter-spacing: 2px; font-family: 'Courier New';")
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(10)

        divider_line = QFrame()
        divider_line.setFixedHeight(1)
        divider_line.setStyleSheet(f"background: {BORDER_COLOR};")
        card_layout.addWidget(divider_line)
        card_layout.addSpacing(6)

        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("Employee ID")
        self.employee_id_input.setFixedHeight(44)
        self.employee_id_input.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                font-family: 'Courier New';
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR}88;
            }}
        """)
        card_layout.addWidget(self.employee_id_input)

        self.company_code_input = QLineEdit()
        self.company_code_input.setPlaceholderText("Company Code")
        self.company_code_input.setEchoMode(QLineEdit.Password)
        self.company_code_input.setFixedHeight(44)
        self.company_code_input.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                font-family: 'Courier New';
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR}88;
            }}
        """)
        card_layout.addWidget(self.company_code_input)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(
            f"color: {ERROR_COLOR}; font-size: 11px; font-family: 'Courier New';")
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(4)

        authenticate_button = QPushButton("⬡  AUTHENTICATE")
        authenticate_button.setFixedHeight(50)
        authenticate_button.setCursor(Qt.PointingHandCursor)
        authenticate_button.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_COLOR}; color: #000000;
                border: none; border-radius: 25px;
                font-size: 14px; font-weight: bold;
                letter-spacing: 1px; padding: 0 28px;
                font-family: 'Courier New';
            }}
            QPushButton:hover {{ background: #d4ff1a; }}
        """)
        authenticate_button.clicked.connect(self._authenticate)
        self.company_code_input.returnPressed.connect(self._authenticate)
        self.employee_id_input.returnPressed.connect(self.company_code_input.setFocus)
        card_layout.addWidget(authenticate_button)

        footer_label = QLabel("AUTHORIZED PERSONNEL ONLY")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet(
            f"color: {MUTED_TEXT_COLOR}; font-size: 9px; "
            f"letter-spacing: 3px; font-family: 'Courier New';")
        card_layout.addSpacing(12)
        card_layout.addWidget(footer_label)

        card_container = QHBoxLayout()
        card_container.addStretch(1)
        card_container.addWidget(card_frame)
        card_container.addStretch(1)
        root_layout.addLayout(card_container)
        root_layout.addStretch(1)

    def _authenticate(self):
        employee_id = self.employee_id_input.text().strip().upper()
        company_code = self.company_code_input.text().strip()

        if CREDENTIALS.get(employee_id) == company_code:
            self.error_label.setVisible(False)
            self.sig_success.emit()
        else:
            self.error_label.setText("ACCESS DENIED  —  INVALID ID OR CODE")
            self.error_label.setVisible(True)
            self.company_code_input.clear()
            self.company_code_input.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())