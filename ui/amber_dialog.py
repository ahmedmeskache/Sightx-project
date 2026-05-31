import sys
import time

from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
)
from PyQt5.QtCore import Qt

BG = "#09090b"
BG_PANEL = "#0f0f12"
BG_INPUT = "#1a1a20"
ACCENT = "#c8ff00"
COLOR_TEXT = "#ffffff"
COLOR_GRAY = "#888899"
COLOR_MUTED = "#333344"
BORDER = "#1c1c24"
COLOR_ALERT = "#ff3344"


class AmberDialog(QDialog):
    def __init__(self, snapshot=None, parent=None):
        super().__init__(parent)
        self.snapshot = snapshot
        self.setWindowTitle("SightX — Missing Child Alert")
        self.setMinimumSize(600, 520)
        self.setStyleSheet(f"background: {BG};")
        self.build_ui()

    def build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(54)
        self.top_bar.setStyleSheet(f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER};")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(24, 0, 24, 0)

        self.title_label = QLabel("🚨  MISSING CHILD ALERT")
        self.title_label.setStyleSheet(
            f"color: {COLOR_ALERT}; font-size: 13px; font-weight: bold; "
            f"letter-spacing: 3px; font-family: 'Courier New';"
        )

        self.close_button = QPushButton("✕  Close")
        self.close_button.setFixedHeight(32)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background: transparent; color: #888888;
                border: 1px solid #333333; border-radius: 16px;
                font-size: 12px; padding: 0 16px;
            }
            QPushButton:hover { color: #ffffff; border-color: #555555; }
            """
        )
        self.close_button.clicked.connect(self.reject)

        self.top_bar_layout.addWidget(self.title_label)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.close_button)

        self.main_layout.addWidget(self.top_bar)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background: {BG};")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(32, 24, 32, 24)
        self.content_layout.setSpacing(16)

        self.warning_label = QLabel("⚠  This will activate live scanning on all detected persons.")
        self.warning_label.setStyleSheet(f"color: {ACCENT}; font-size: 11px; font-family: 'Courier New';")
        self.content_layout.addWidget(self.warning_label)

        self.content_layout.addWidget(self.section_label("CHILD DESCRIPTION"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "e.g. 7-year-old boy, blue jacket, red backpack, black hair, approximately 120cm tall..."
        )
        self.description_edit.setFixedHeight(100)
        self.description_edit.setStyleSheet(
            f"""
            QTextEdit {{
                background: {BG_INPUT};
                color: {COLOR_TEXT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }}
            """
        )
        self.content_layout.addWidget(self.description_edit)

        self.content_layout.addWidget(self.section_label("LAST SEEN LOCATION"))
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g. Camera 3 — Main Gate, 14:32")
        self.location_input.setFixedHeight(40)
        self.location_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: {BG_INPUT};
                color: {COLOR_TEXT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }}
            """
        )
        self.content_layout.addWidget(self.location_input)

        self.content_layout.addWidget(self.section_label("CONTACT / REPORTER"))
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("e.g. Officer Johnson — Badge #4421 — +1-555-0199")
        self.contact_input.setFixedHeight(40)
        self.contact_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: {BG_INPUT};
                color: {COLOR_TEXT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }}
            """
        )
        self.content_layout.addWidget(self.contact_input)

        self.content_layout.addStretch()

        self.button_row = QHBoxLayout()
        self.button_row.addStretch()

        self.activate_button = QPushButton("  ACTIVATE AMBER SCAN")
        self.activate_button.setFixedHeight(46)
        self.activate_button.setCursor(Qt.PointingHandCursor)
        self.activate_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {COLOR_ALERT}; color: #ffffff;
                border: none; border-radius: 23px;
                font-size: 13px; font-weight: bold;
                padding: 0 28px; font-family: 'Courier New';
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: #ff5566; }}
            """
        )
        self.activate_button.clicked.connect(self.accept)

        self.button_row.addWidget(self.activate_button)
        self.content_layout.addLayout(self.button_row)

        self.footer_label = QLabel("AUTHORIZED PERSONNEL ONLY")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet(
            f"color: {COLOR_MUTED}; font-size: 9px; letter-spacing: 3px; font-family: 'Courier New';"
        )
        self.content_layout.addSpacing(12)
        self.content_layout.addWidget(self.footer_label)

        self.main_layout.addWidget(self.content_widget)

    def section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            f"""
            color: {COLOR_GRAY};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            font-family: 'Courier New';
            padding-bottom: 4px;
            """
        )
        return label

    def get_data(self) -> dict:
        return {
            "description": self.description_edit.toPlainText().strip(),
            "location": self.location_input.text().strip(),
            "contact": self.contact_input.text().strip(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = AmberDialog()
    if dialog.exec_() == dialog.Accepted:
        print("Accepted:", dialog.get_data())
    else:
        print("Rejected")
    sys.exit(app.exec_())