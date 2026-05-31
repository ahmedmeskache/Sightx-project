import sys, os, time, datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy, QComboBox
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

SEVERITY_COLOR = {
    "CRITICAL": "#ff3344",
    "HIGH": "#ff8800",
    "MEDIUM": "#ffcc00",
    "NORMAL": "#00aaff",
}


def alert_severity(alert_type):
    return {
        "ZONE": "CRITICAL",
        "AMBER": "CRITICAL",
        "SPEED": "HIGH",
        "RUNNING": "MEDIUM",
        "LOITER": "NORMAL",
    }.get(str(alert_type).upper(), "NORMAL")


class SeverityBadge(QLabel):
    def __init__(self, severity, parent=None):
        super().__init__(parent)
        color = SEVERITY_COLOR.get(severity, "#888")
        self.setText(severity)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(82, 22)
        self.setStyleSheet(f"""
            QLabel {{
                background: {color}22;
                color: {color};
                border: 1px solid {color}66;
                border-radius: 11px;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                font-family: 'Courier New';
            }}
        """)


class DateHeader(QWidget):
    def __init__(self, date_text, count, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet(f"background: {PANEL_COLOR};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel(date_text)
        title_label.setStyleSheet(
            f"color: {ACCENT_COLOR}; font-size: 12px; font-weight: bold; "
            f"letter-spacing: 2px; font-family: 'Courier New';")

        count_label = QLabel(f"{count} events")
        count_label.setStyleSheet(
            f"color: {MUTED_TEXT_COLOR}; font-size: 11px; font-family: 'Courier New';")

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"color: {BORDER_COLOR};")
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(title_label)
        layout.addSpacing(16)
        layout.addWidget(separator)
        layout.addSpacing(16)
        layout.addWidget(count_label)


class AlertRow(QWidget):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QWidget {{
                background: {CARD_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QWidget:hover {{ background: #18181f; }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(20)

        alert_type = entry.get("type", "")
        severity = alert_severity(alert_type)
        color = SEVERITY_COLOR.get(severity, SECONDARY_TEXT_COLOR)

        time_label = QLabel(entry.get("time", ""))
        time_label.setFixedWidth(78)
        time_label.setStyleSheet(
            f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px; font-family: 'Courier New';")

        type_label = QLabel(alert_type)
        type_label.setFixedWidth(90)
        type_label.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: bold; "
            f"font-family: 'Courier New';")

        object_label = QLabel(entry.get("cls", "Unknown"))
        object_label.setFixedWidth(80)
        object_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px;")

        raw_id = entry.get("id", entry.get("track_id", "?"))
        id_label = QLabel(f"ID {raw_id}")
        id_label.setFixedWidth(55)
        id_label.setStyleSheet(
            f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px; font-family: 'Courier New';")

        details_label = QLabel(entry.get("details", ""))
        details_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px;")
        details_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        badge = SeverityBadge(severity)

        layout.addWidget(time_label)
        layout.addWidget(type_label)
        layout.addWidget(object_label)
        layout.addWidget(id_label)
        layout.addWidget(details_label)
        layout.addStretch()
        layout.addWidget(badge)


class HistoryWindow(QMainWindow):
    sig_back = pyqtSignal()

    def __init__(self, alert_log=None):
        super().__init__()
        self.setWindowTitle("SightX — Detection History")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(f"background: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        self.alert_log = (
            alert_log
            or self._load_from_disk()
            or self._demo_entries()
        )
        self._build_interface()

    def _load_from_disk(self):
        try:
            sys.path.insert(
                0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import config
            path = os.path.join(config.OUTPUTS_DIR, "alert_log.txt")
            if not os.path.exists(path):
                return None
            entries = []
            with open(path, "r") as handle:
                for line in handle:
                    line = line.strip()
                    if (not line
                            or line.startswith("=")
                            or line.startswith("SIGHTX")
                            or line.startswith("Total")):
                        continue
                    try:
                        timestamp_end = line.index("]")
                        timestamp_text = line[1:timestamp_end].strip()
                        parts = line[timestamp_end + 1:].strip().split()
                        alert_type = parts[0] if parts else "UNKNOWN"
                        track_id = parts[2] if len(parts) > 2 else "?"
                        details = " ".join(parts[3:]) if len(parts) > 3 else ""
                        date_value, time_value = timestamp_text.split(" ") if " " in timestamp_text else (timestamp_text, "")
                        entries.append({
                            "date": date_value,
                            "time": time_value,
                            "type": alert_type,
                            "cls": "Unknown",
                            "id": track_id,
                            "details": details,
                        })
                    except Exception:
                        continue
            return entries if entries else None
        except Exception:
            return None

    def _demo_entries(self):
        today = time.strftime("%Y-%m-%d")
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        two_days_ago = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        return [
            {"date": today, "time": "08:14:22", "type": "ZONE", "cls": "Person", "id": 3, "details": "Restricted area breach"},
            {"date": today, "time": "09:02:11", "type": "SPEED", "cls": "Car", "id": 7, "details": "94.2 km/h"},
            {"date": today, "time": "11:45:08", "type": "RUNNING", "cls": "Person", "id": 12, "details": "Abnormal movement"},
            {"date": today, "time": "14:30:55", "type": "LOITER", "cls": "Person", "id": 5, "details": "Loitering > 60s"},
            {"date": yesterday, "time": "07:33:10", "type": "SPEED", "cls": "Car", "id": 2, "details": "112.7 km/h"},
            {"date": yesterday, "time": "10:22:30", "type": "ZONE", "cls": "Person", "id": 8, "details": "Restricted area breach"},
            {"date": yesterday, "time": "13:05:17", "type": "LOITER", "cls": "Person", "id": 4, "details": "Loitering > 45s"},
            {"date": two_days_ago, "time": "09:10:00", "type": "RUNNING", "cls": "Person", "id": 6, "details": "Abnormal movement"},
            {"date": two_days_ago, "time": "15:44:22", "type": "SPEED", "cls": "Car", "id": 9, "details": "88.0 km/h"},
        ]

    def _build_interface(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(
            f"background: {PANEL_COLOR}; border-bottom: 1px solid {BORDER_COLOR};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 0, 28, 0)

        back_button = QPushButton("← Back")
        back_button.setFixedHeight(36)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {SECONDARY_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR}; border-radius: 18px;
                font-size: 13px; font-family: 'Courier New'; padding: 0 18px;
            }}
            QPushButton:hover {{ color: {ACCENT_COLOR}; border-color: {ACCENT_COLOR}44; }}
        """)
        back_button.clicked.connect(self.sig_back.emit)

        title = QLabel("DETECTION HISTORY")
        title.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 15px; font-weight: bold; "
            f"letter-spacing: 4px; font-family: 'Courier New';")

        self.filter_box = QComboBox()
        self.filter_box.addItems([
            "All Severities", "CRITICAL", "HIGH", "MEDIUM", "NORMAL"
        ])
        self.filter_box.setFixedHeight(36)
        self.filter_box.setStyleSheet(f"""
            QComboBox {{
                background: {INPUT_COLOR}; color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR}; border-radius: 6px;
                padding: 0 12px; font-size: 13px; min-width: 160px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {CARD_COLOR}; color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                selection-background-color: {INPUT_COLOR};
            }}
        """)
        self.filter_box.currentTextChanged.connect(self._refresh)

        self.total_label = QLabel()
        self.total_label.setStyleSheet(
            f"color: {MUTED_TEXT_COLOR}; font-size: 12px; font-family: 'Courier New';")

        header_layout.addWidget(back_button)
        header_layout.addSpacing(24)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.total_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.filter_box)
        root_layout.addWidget(header)

        legend_bar = QWidget()
        legend_bar.setFixedHeight(42)
        legend_bar.setStyleSheet(f"background: {PANEL_COLOR};")
        legend_layout = QHBoxLayout(legend_bar)
        legend_layout.setContentsMargins(28, 0, 28, 0)
        legend_layout.setSpacing(24)
        for severity, color in SEVERITY_COLOR.items():
            label = QLabel(f"● {severity}")
            label.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: bold; "
                f"letter-spacing: 1px; font-family: 'Courier New';")
            legend_layout.addWidget(label)
        legend_layout.addStretch()
        root_layout.addWidget(legend_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ background: {BACKGROUND_COLOR}; border: none; }}
            QScrollBar:vertical {{
                background: {BACKGROUND_COLOR}; width: 5px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {MUTED_TEXT_COLOR}; border-radius: 3px;
            }}
        """)
        root_layout.addWidget(self.scroll_area)
        self._refresh()

    def _refresh(self):
        selected = self.filter_box.currentText()
        visible_entries = self.alert_log
        if selected != "All Severities":
            visible_entries = [
                entry for entry in visible_entries
                if alert_severity(entry.get("type", "")) == selected
            ]

        self.total_label.setText(f"{len(visible_entries)} events")

        from collections import OrderedDict
        groups = OrderedDict()
        for entry in sorted(
            visible_entries,
            key=lambda x: (x.get("date", ""), x.get("time", "")),
            reverse=True,
        ):
            date_key = entry.get("date", "Unknown")
            groups.setdefault(date_key, []).append(entry)

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background: {BACKGROUND_COLOR};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 20)
        content_layout.setSpacing(0)

        if not visible_entries:
            notice = QLabel("No events found.")
            notice.setAlignment(Qt.AlignCenter)
            notice.setStyleSheet(
                f"color: {MUTED_TEXT_COLOR}; font-size: 16px; padding: 60px;")
            content_layout.addWidget(notice)
        else:
            today_date = datetime.date.today()
            for date_key, entries in groups.items():
                try:
                    parsed_date = datetime.date.fromisoformat(date_key)
                    if parsed_date == today_date:
                        header_text = f"TODAY  —  {date_key}"
                    elif parsed_date == today_date - datetime.timedelta(days=1):
                        header_text = f"YESTERDAY  —  {date_key}"
                    else:
                        header_text = parsed_date.strftime("%A  —  %d %B %Y").upper()
                except Exception:
                    header_text = date_key

                content_layout.addWidget(DateHeader(header_text, len(entries)))
                for entry in entries:
                    content_layout.addWidget(AlertRow(entry))

        content_layout.addStretch()
        self.scroll_area.setWidget(content_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistoryWindow()
    window.show()
    sys.exit(app.exec_())