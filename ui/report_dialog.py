import sys, os, time

from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QLineEdit,
    QScrollArea, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

BACKGROUND_COLOR = "#09090b"
PAPER_COLOR = "#f7f5ef"
SECTION_COLOR = "#eeeae0"
TEXT_COLOR = "#1a1a1a"
LIGHT_TEXT_COLOR = "#666666"
MUTED_TEXT_COLOR = "#aaaaaa"
ACCENT_COLOR = "#c8ff00"
LINE_COLOR = "#d0cdc4"


def section_label(text):
    label = QLabel(text)
    label.setStyleSheet(f"""
        color: {LIGHT_TEXT_COLOR};
        font-size: 9px;
        font-weight: bold;
        letter-spacing: 2px;
        font-family: 'Courier New';
        border-bottom: 1px solid {LINE_COLOR};
        padding-bottom: 3px;
    """)
    return label


def field_label(text):
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {LIGHT_TEXT_COLOR}; font-size: 10px; "
        f"font-family: 'Courier New'; letter-spacing: 1px;")
    return label


class ImageBox(QLabel):
    def __init__(self, placeholder, width=200, height=140, parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.pixmap_source = None
        self._render()

    def _render(self):
        if self.pixmap_source:
            self.setPixmap(
                self.pixmap_source.scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setStyleSheet(
                f"border: 2px solid {LINE_COLOR}; "
                f"border-radius: 4px; background: {SECTION_COLOR};")
        else:
            self.setText(f"+ {self.placeholder}")
            self.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {LINE_COLOR};
                    border-radius: 4px;
                    background: {SECTION_COLOR};
                    color: {MUTED_TEXT_COLOR};
                    font-size: 11px;
                    font-family: 'Courier New';
                }}
            """)

    def set_pixmap(self, pixmap):
        self.pixmap_source = pixmap
        self._render()

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.set_pixmap(QPixmap(path))


class LinedField(QTextEdit):
    def __init__(self, placeholder="", height=100, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: {TEXT_COLOR};
                border: none;
                border-bottom: 1px solid {LINE_COLOR};
                font-size: 13px;
                font-family: 'Georgia', serif;
                padding: 4px 2px;
            }}
        """)


class SingleLine(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(placeholder, parent)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {TEXT_COLOR};
                border: none;
                border-bottom: 1px solid {LINE_COLOR};
                font-size: 13px;
                font-family: 'Georgia', serif;
                padding: 4px 2px;
            }}
        """)


class ReportDialog(QDialog):
    def __init__(self, snapshot=None, parent=None):
        super().__init__(parent)
        self.snapshot = snapshot
        self.setWindowTitle("SightX — File an Incident Report")
        self.setMinimumSize(860, 740)
        self.setStyleSheet(f"background: {BACKGROUND_COLOR};")
        self._build_interface()

    def _build_interface(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setFixedHeight(54)
        top_bar.setStyleSheet("background: #0f0f12; border-bottom: 1px solid #1c1c22;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(24, 0, 24, 0)

        title_label = QLabel("FILE AN INCIDENT REPORT")
        title_label.setStyleSheet(
            f"color: {ACCENT_COLOR}; font-size: 13px; font-weight: bold; "
            f"letter-spacing: 4px; font-family: 'Courier New';")

        save_button = QPushButton("  Save Report")
        save_button.setFixedHeight(32)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_COLOR}; color: #000000;
                border: none; border-radius: 16px;
                font-size: 12px; font-weight: bold;
                padding: 0 20px; font-family: 'Courier New';
            }}
            QPushButton:hover {{ background: #d4ff1a; }}
        """)
        save_button.clicked.connect(self._save)

        close_button = QPushButton("✕  Close")
        close_button.setFixedHeight(32)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent; color: #888888;
                border: 1px solid #333333; border-radius: 16px;
                font-size: 12px; padding: 0 16px;
            }
            QPushButton:hover { color: #ffffff; border-color: #555555; }
        """)
        close_button.clicked.connect(self.reject)

        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(save_button)
        top_bar_layout.addSpacing(10)
        top_bar_layout.addWidget(close_button)
        outer_layout.addWidget(top_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ background: {BACKGROUND_COLOR}; border: none; }}
            QScrollBar:vertical {{ background: {BACKGROUND_COLOR}; width: 5px; }}
            QScrollBar::handle:vertical {{
                background: #333333; border-radius: 3px;
            }}
        """)
        outer_layout.addWidget(scroll_area)

        paper = QWidget()
        paper.setStyleSheet(f"background: {PAPER_COLOR}; border-radius: 4px;")
        paper_layout = QVBoxLayout(paper)
        paper_layout.setContentsMargins(52, 48, 52, 52)
        paper_layout.setSpacing(22)

        header_layout = QHBoxLayout()
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        brand_label = QLabel("SIGHTX")
        brand_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 22px; font-weight: 900; "
            f"letter-spacing: 5px; font-family: 'Courier New';")
        subtitle_label = QLabel("Security Incident Report")
        subtitle_label.setStyleSheet(
            f"color: {LIGHT_TEXT_COLOR}; font-size: 12px; font-family: 'Courier New';")
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(subtitle_label)

        metadata_layout = QVBoxLayout()
        metadata_layout.setSpacing(4)
        metadata_layout.setAlignment(Qt.AlignRight)
        for metadata_text in [
            f"Date:      {time.strftime('%Y-%m-%d')}",
            f"Time:      {time.strftime('%H:%M:%S')}",
            f"Report #:  {time.strftime('%Y%m%d%H%M%S')}",
        ]:
            metadata_label = QLabel(metadata_text)
            metadata_label.setAlignment(Qt.AlignRight)
            metadata_label.setStyleSheet(
                f"color: {TEXT_COLOR}; font-size: 11px; font-family: 'Courier New';")
            metadata_layout.addWidget(metadata_label)

        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        header_layout.addLayout(metadata_layout)
        paper_layout.addLayout(header_layout)

        divider_line = QFrame()
        divider_line.setFrameShape(QFrame.HLine)
        divider_line.setFixedHeight(2)
        divider_line.setStyleSheet(f"background: {TEXT_COLOR};")
        paper_layout.addWidget(divider_line)

        paper_layout.addWidget(section_label("01  —  INCIDENT CAPTURE"))
        scene_layout = QHBoxLayout()
        scene_layout.setSpacing(18)

        self.scene_image = ImageBox("Click to add scene screenshot", 340, 200)
        if self.snapshot:
            self.scene_image.set_pixmap(self.snapshot)

        scene_detail_layout = QVBoxLayout()
        scene_detail_layout.setSpacing(10)
        scene_detail_layout.addWidget(field_label("Capture Date & Time"))
        self.capture_date = SingleLine(time.strftime("%Y-%m-%d  %H:%M:%S"))
        scene_detail_layout.addWidget(self.capture_date)
        scene_detail_layout.addWidget(field_label("Camera / Location"))
        self.camera_location = SingleLine("e.g. Camera 1 — Main Gate")
        scene_detail_layout.addWidget(self.camera_location)
        scene_detail_layout.addStretch()

        scene_layout.addWidget(self.scene_image)
        scene_layout.addLayout(scene_detail_layout)
        scene_layout.addStretch()
        paper_layout.addLayout(scene_layout)

        paper_layout.addWidget(section_label("02  —  EVIDENCE"))
        evidence_layout = QHBoxLayout()
        evidence_layout.setSpacing(24)

        plate_layout = QVBoxLayout()
        plate_layout.setSpacing(6)
        plate_layout.addWidget(field_label("Vehicle / Licence Plate"))
        self.plate_image = ImageBox("Add plate photo", 210, 130)
        self.license_plate = SingleLine("Plate number (if readable)")
        plate_layout.addWidget(self.plate_image)
        plate_layout.addWidget(self.license_plate)

        suspect_layout = QVBoxLayout()
        suspect_layout.setSpacing(6)
        suspect_layout.addWidget(field_label("Suspect / Person"))
        self.face_image = ImageBox("Add face / suspect photo", 210, 130)
        self.suspect_description = SingleLine("Description (clothing, height, build…)")
        suspect_layout.addWidget(self.face_image)
        suspect_layout.addWidget(self.suspect_description)

        evidence_layout.addLayout(plate_layout)
        evidence_layout.addLayout(suspect_layout)
        evidence_layout.addStretch()
        paper_layout.addLayout(evidence_layout)

        paper_layout.addWidget(section_label("03  —  WHAT HAPPENED"))
        self.event_description = LinedField(
            "Describe the incident in detail…\n"
            "e.g. At 14:32 a vehicle was detected speeding at 112 km/h "
            "through camera 3 near the main gate…",
            height=120)
        paper_layout.addWidget(self.event_description)

        paper_layout.addWidget(section_label("04  —  ADDITIONAL INFORMATION"))
        self.additional_notes = LinedField(
            "Any additional notes, witness info, follow-up actions required…",
            height=90)
        paper_layout.addWidget(self.additional_notes)

        signature_layout = QHBoxLayout()
        signature_layout.setSpacing(0)
        for label_text in ["Officer Signature", "Badge / ID", "Supervisor"]:
            column = QVBoxLayout()
            column.setSpacing(4)
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFixedHeight(1)
            line.setStyleSheet(f"background: {LINE_COLOR};")
            signature_label = QLabel(label_text)
            signature_label.setStyleSheet(
                f"color: {MUTED_TEXT_COLOR}; font-size: 10px; "
                f"font-family: 'Courier New'; letter-spacing: 1px;")
            column.addSpacing(30)
            column.addWidget(line)
            column.addWidget(signature_label)
            signature_layout.addLayout(column)
            signature_layout.addSpacing(36)
        signature_layout.addStretch()
        paper_layout.addLayout(signature_layout)

        footer = QLabel("CONFIDENTIAL  —  SIGHTX SECURITY SYSTEMS")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(
            f"color: {MUTED_TEXT_COLOR}; font-size: 9px; "
            f"letter-spacing: 3px; font-family: 'Courier New';")
        paper_layout.addWidget(footer)

        wrapper = QWidget()
        wrapper.setStyleSheet(f"background: {BACKGROUND_COLOR};")
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(40, 32, 40, 32)
        wrapper_layout.addWidget(paper)
        scroll_area.setWidget(wrapper)

    def _save(self):
        try:
            sys.path.insert(
                0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import config
            out_dir = config.OUTPUTS_DIR
        except Exception:
            out_dir = os.path.join(
                os.path.dirname(__file__), "..", "outputs")

        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(
            out_dir, f"report_{time.strftime('%Y%m%d_%H%M%S')}.txt")

        with open(path, "w", encoding="utf-8") as handle:
            handle.write("=" * 60 + "\n")
            handle.write("       SIGHTX — INCIDENT REPORT\n")
            handle.write("=" * 60 + "\n\n")
            handle.write(f"Date / Time  : {self.capture_date.text()}\n")
            handle.write(f"Camera       : {self.camera_location.text()}\n")
            handle.write(f"Plate        : {self.license_plate.text()}\n")
            handle.write(f"Suspect      : {self.suspect_description.text()}\n\n")
            handle.write("WHAT HAPPENED:\n")
            handle.write(self.event_description.toPlainText() + "\n\n")
            handle.write("ADDITIONAL INFORMATION:\n")
            handle.write(self.additional_notes.toPlainText() + "\n")
            handle.write("\n" + "=" * 60 + "\n")

        try:
            os.startfile(path)
        except Exception:
            pass

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ReportDialog()
    dialog.exec_()
