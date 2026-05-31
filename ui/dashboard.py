import sys
import os
import time
import cv2
import numpy as np

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QImage, QPixmap, QColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from detector import Detector
from tracker import Tracker
from alert import AlertSystem
from pose_analyzer import PoseAnalyzer
from ai_engine import AnomalyEngine
from amber_engine import AmberEngine

BG = "#09090b"
BG_PANEL = "#0f0f12"
BG_CARD = "#141418"
BG_INPUT = "#1a1a20"
ACCENT = "#c8ff00"
ACCENT2 = "#00aaff"
COLOR_RED = "#ff3344"
TEXT_WHITE = "#ffffff"
TEXT_GRAY = "#888899"
TEXT_MUTED = "#333344"
BORDER = "#1c1c24"
RED = "#FF4D4D"

SEVERITY_COLOR = {
    "SPEED": "#ff8800",
    "ZONE": COLOR_RED,
    "RUNNING": "#ffcc00",
    "LOITER": ACCENT2,
    "AMBER": COLOR_RED,
}


class VideoWorker(QObject):
    frame_ready = pyqtSignal(np.ndarray, list)
    stats_updated = pyqtSignal(dict)
    alert_triggered = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, amber_engine=None):
        super().__init__()
        self.running = False
        self.amber_engine = amber_engine

    def start(self):
        self.running = True

        detector = Detector()
        tracker = Tracker()
        alert_system = AlertSystem()
        pose_analyzer = PoseAnalyzer()
        ai_engine = AnomalyEngine()

        source = 0
        try:
            for f in sorted(os.listdir(config.VIDEOS_DIR)):
                if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    source = os.path.join(config.VIDEOS_DIR, f)
                    break
        except Exception:
            pass

        cap = cv2.VideoCapture(source)
        native_fps = cap.get(cv2.CAP_PROP_FPS) or config.TARGET_FPS
        if native_fps <= 0 or native_fps > 60:
            native_fps = 30.0
        frame_delay = 1.0 / native_fps
        frame_count = 0
        last_detections = []

        while self.running:
            loop_start = time.time()

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_count += 1

            frame = cv2.resize(frame, (config.RESIZE_WIDTH, config.RESIZE_HEIGHT))

            if frame_count % config.SKIP_FRAMES != 0:
                if last_detections is not None:
                    annotated = detector.draw(frame, last_detections)
                    self.frame_ready.emit(annotated, last_detections)

                elapsed = time.time() - loop_start
                sleep_time = frame_delay - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                continue

            detections = detector.detect(frame)
            detections = tracker.update(detections, native_fps)
            last_detections = detections

            active_ids = []
            for d in detections:
                tid = d.get("track_id")
                if tid is not None:
                    active_ids.append(tid)

                if d["cls"] == 0 and tid is not None:
                    pose_result = pose_analyzer.analyze_person(frame, d["bbox"])
                    d["pose"] = pose_result

                    if (
                        pose_result["pose_detected"]
                        and pose_result["activity"] == "running"
                        and pose_result["confidence"] > 0.75
                        and not d.get("alert")
                    ):
                        d["alert"] = True
                        d["alert_type"] = "RUNNING"

                    if self.amber_engine and self.amber_engine.active:
                        self.amber_engine.scan(d, frame)

            pose_analyzer.cleanup(active_ids)

            for d in detections:
                if d.get("alert"):
                    alert_system.trigger(frame, d)
                    self.alert_triggered.emit(
                        {
                            "date": time.strftime("%Y-%m-%d"),
                            "time": time.strftime("%H:%M:%S"),
                            "type": d.get("alert_type", "UNKNOWN"),
                            "id": d.get("track_id", "?"),
                            "cls": "Car" if d["cls"] == 2 else "Person",
                            "details": (
                                f"Speed: {d.get('speed', 0)} km/h"
                                if d["cls"] == 2
                                else f"Time: {d.get('elapsed', 0)}s"
                            ),
                        }
                    )

            annotated = detector.draw(frame, detections)

            for d in detections:
                if d.get("pose") and d["pose"]["pose_detected"]:
                    annotated = pose_analyzer.draw_pose(
                        annotated, d["pose"]["keypoints"], d["pose"]["activity"]
                    )

            loop_elapsed = time.time() - loop_start
            fps = 1.0 / loop_elapsed if loop_elapsed > 0 else 0

            self.frame_ready.emit(annotated, detections)
            self.stats_updated.emit(
                {
                    "fps": fps,
                    "persons": sum(1 for d in detections if d["cls"] == 0),
                    "cars": sum(1 for d in detections if d["cls"] == 2),
                    "alerts": len(alert_system.alert_log),
                }
            )

            elapsed = time.time() - loop_start
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        alert_system.save_log()
        cap.release()
        self.finished.emit()

    def stop(self):
        self.running = False


class StatCard(QFrame):
    def __init__(self, title, value, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(86)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 10px;
                border: 1px solid {BORDER};
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(2)
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        caption = QLabel(title)
        caption.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 10px; letter-spacing: 2px; font-family: 'Courier New';"
        )
        layout.addWidget(self.value_label)
        layout.addWidget(caption)

    def update_value(self, v):
        self.value_label.setText(str(v))


class HistoryTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Date", "Time", "Type", "Object", "ID", "Details"])
        self.setStyleSheet(
            f"""
            QTableWidget {{
                background: {BG_CARD}; color: {TEXT_WHITE};
                border: none; gridline-color: {BORDER}; font-size: 12px;
            }}
            QHeaderView::section {{
                background: {BG_PANEL}; color: {TEXT_GRAY};
                border: none; border-bottom: 1px solid {BORDER};
                padding: 8px; font-size: 10px; font-weight: bold;
                letter-spacing: 1px; font-family: 'Courier New';
            }}
            QTableWidget::item {{
                padding: 6px 10px; border-bottom: 1px solid {BORDER};
            }}
            QTableWidget::item:selected {{
                background: #1a1a2a; color: {ACCENT};
            }}
            QScrollBar:vertical {{
                background: {BG}; width: 5px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {TEXT_MUTED}; border-radius: 3px;
            }}
            """
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)

    def add_alert(self, alert):
        self.insertRow(0)
        col = SEVERITY_COLOR.get(alert.get("type", ""), TEXT_GRAY)
        for i, val in enumerate([
            alert.get("date", ""),
            alert.get("time", ""),
            alert.get("type", ""),
            alert.get("cls", ""),
            str(alert.get("id", "?")),
            alert.get("details", ""),
        ]):
            item = QTableWidgetItem(val)
            item.setForeground(QColor(col if i == 2 else TEXT_WHITE))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(0, i, item)

    def export(self):
        os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
        path = os.path.join(config.OUTPUTS_DIR, f"history_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("SIGHTX  ALERT HISTORY\n" + "=" * 60 + "\n")
            for row in range(self.rowCount()):
                vals = [self.item(row, c).text() for c in range(self.columnCount())]
                f.write("  ".join(f"{v:<14}" for v in vals) + "\n")
        print(f"[EXPORT] History saved: {path}")
        return path


class DashboardWindow(QMainWindow):
    sig_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SightX — Live Camera")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(f"background: {BG}; color: {TEXT_WHITE};")

        self.alert_log = []
        self.last_frame_pix = None
        self.amber_engine = AmberEngine()

        self.start_video()
        self.build_ui()

    def start_video(self):
        self.vthread = QThread()
        self.vworker = VideoWorker(amber_engine=self.amber_engine)
        self.vworker.moveToThread(self.vthread)
        self.vthread.started.connect(self.vworker.start)
        self.vworker.frame_ready.connect(self.on_frame)
        self.vworker.stats_updated.connect(self.on_stats)
        self.vworker.alert_triggered.connect(self.on_alert)
        self.vthread.start()

    def build_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        rv = QVBoxLayout(cw)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        hdr = QWidget()
        hdr.setFixedHeight(60)
        hdr.setStyleSheet(f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 0, 24, 0)

        back = QPushButton("← Back")
        back.setFixedHeight(34)
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent; color: {TEXT_GRAY};
                border: 1px solid {BORDER}; border-radius: 17px;
                font-size: 12px; padding: 0 16px; font-family: 'Courier New';
            }}
            QPushButton:hover {{ color: {ACCENT}; border-color: {ACCENT}44; }}
            """
        )
        back.clicked.connect(self.sig_back.emit)

        title = QLabel("LIVE SURVEILLANCE")
        title.setStyleSheet(
            f"color: {TEXT_WHITE}; font-size: 15px; font-weight: bold; letter-spacing: 4px; font-family: 'Courier New';"
        )

        self.live_indicator = QLabel("● LIVE")
        self.live_indicator.setStyleSheet(
            f"color: {ACCENT}; font-size: 12px; font-weight: bold; font-family: 'Courier New';"
        )

        self.amber_btn = QPushButton("🚨  Amber Alert")
        self.amber_btn.setFixedHeight(36)
        self.amber_btn.setCursor(Qt.PointingHandCursor)
        self.amber_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {COLOR_RED}; color: #ffffff;
                border: none; border-radius: 18px;
                font-size: 13px; font-weight: bold;
                padding: 0 22px; font-family: 'Courier New';
            }}
            QPushButton:hover {{ background: #ff5566; }}
            """
        )
        self.amber_btn.clicked.connect(self.open_amber)

        self.report_btn = QPushButton("📋  File a Report")
        self.report_btn.setFixedHeight(36)
        self.report_btn.setCursor(Qt.PointingHandCursor)
        self.report_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {ACCENT}; color: #000000;
                border: none; border-radius: 18px;
                font-size: 13px; font-weight: bold;
                padding: 0 22px; font-family: 'Courier New';
            }}
            QPushButton:hover {{ background: #d4ff1a; }}
            """
        )
        self.report_btn.clicked.connect(self.open_report)

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 12px; font-family: 'Courier New';")
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        hl.addWidget(back)
        hl.addSpacing(20)
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(self.live_indicator)
        hl.addSpacing(16)
        hl.addWidget(self.amber_btn)
        hl.addSpacing(10)
        hl.addWidget(self.report_btn); hl.addSpacing(20)
        hl.addWidget(self.clock_label)
        rv.addWidget(hdr)

        # Body
        body = QWidget()
        bl = QHBoxLayout(body)
        bl.setContentsMargins(16, 16, 16, 16); bl.setSpacing(16)
        left = QVBoxLayout(); left.setSpacing(14)

        # Video panel
        vf = QFrame()
        vf.setStyleSheet(
            f"background: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        vfl = QVBoxLayout(vf)
        vfl.setContentsMargins(10, 10, 10, 10); vfl.setSpacing(8)
        vtitle = QLabel("📹  CAMERA FEED")
        vtitle.setStyleSheet(
            f"color: {TEXT_GRAY}; font-size: 10px; "
            f"letter-spacing: 2px; font-family: 'Courier New';")
        vfl.addWidget(vtitle)
        self.video_label = QLabel("Connecting to camera…")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumHeight(340)
        self.video_label.setStyleSheet("background: #000; border-radius: 8px; color: #555; font-size: 14px;")
        vfl.addWidget(self.video_label)
        left.addWidget(vf)

        # Stat cards
        sf = QFrame(); sf.setStyleSheet("background: transparent;")
        sl = QHBoxLayout(sf)
        sl.setContentsMargins(0, 0, 0, 0); sl.setSpacing(12)
        self.stat_fps = StatCard("FPS", "0", ACCENT2)
        self.stat_persons = StatCard("PERSONS", "0", ACCENT)
        self.stat_vehicles = StatCard("VEHICLES", "0", ACCENT2)
        self.stat_alerts = StatCard("TOTAL ALERTS", "0", COLOR_RED)
        for c in [self.stat_fps, self.stat_persons, self.stat_vehicles, self.stat_alerts]:
            sl.addWidget(c)
        left.addWidget(sf)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(200)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: {BG_PANEL}; color: {TEXT_GRAY};
                padding: 8px 20px;
                border: 1px solid {BORDER};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                font-size: 11px;
                font-family: 'Courier New';
                letter-spacing: 1px;
            }}
            QTabBar::tab:selected {{
                background: {BG_CARD};
                color: {ACCENT};
                border-bottom: 2px solid {ACCENT};
            }}
        """)

        # Recent tab
        rw = QWidget(); rw.setStyleSheet(f"background: {BG_CARD};")
        rl = QVBoxLayout(rw); rl.setContentsMargins(16, 10, 16, 10)
        self.recent_label = QLabel("No alerts yet.")
        self.recent_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.recent_label.setWordWrap(True)
        self.recent_label.setAlignment(Qt.AlignTop)
        rl.addWidget(self.recent_label)

        # History tab
        hw = QWidget(); hw.setStyleSheet(f"background: {BG_CARD};")
        hbl = QVBoxLayout(hw)
        hbl.setContentsMargins(8, 8, 8, 8); hbl.setSpacing(8)
        tbar = QHBoxLayout()
        self.count_label = QLabel("0 alerts")
        self.count_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 11px; font-weight: bold; font-family: 'Courier New';")
        exp_btn = QPushButton("Export TXT")
        exp_btn.setFixedHeight(26); exp_btn.setCursor(Qt.PointingHandCursor)
        exp_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_INPUT}; color: {TEXT_WHITE};
                border: 1px solid {BORDER}; border-radius: 4px;
                font-size: 11px; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
        """)
        exp_btn.clicked.connect(lambda: self.history_table.export())
        clr_btn = QPushButton("Clear")
        clr_btn.setFixedHeight(26); clr_btn.setCursor(Qt.PointingHandCursor)
        clr_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BG_INPUT}; color: {TEXT_WHITE};
                border: 1px solid {BORDER}; border-radius: 4px;
                font-size: 11px; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; color: {RED}; }}
        """)
        clr_btn.clicked.connect(self.clear_history)
        tbar.addWidget(self.count_label); tbar.addStretch()
        tbar.addWidget(exp_btn); tbar.addWidget(clr_btn)
        hbl.addLayout(tbar)
        self.history_table = HistoryTable()
        hbl.addWidget(self.history_table)

        self.tabs.addTab(rw, "🚨  RECENT")
        self.tabs.addTab(hw, "📋  ALL HISTORY")
        left.addWidget(self.tabs)

        bl.addLayout(left, stretch=7)
        rv.addWidget(body)

    # Slots

    def update_clock(self):
        self.clock_label.setText(time.strftime("%d %b %Y  ·  %H:%M:%S"))

    def on_frame(self, frame, dets):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        img = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.last_frame_pix = pix
        self.video_label.setPixmap(
            pix.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def on_stats(self, s):
        self.stat_fps.update_value(f"{s['fps']:.0f}")
        self.stat_persons.update_value(s["persons"])
        self.stat_vehicles.update_value(s["cars"])
        self.stat_alerts.update_value(s["alerts"])

    def on_alert(self, alert):
        self.alert_log.append(alert)
        self.history_table.add_alert(alert)
        self.count_label.setText(f"{len(self.alert_log)} alerts")
        lines = []
        for a in reversed(self.alert_log[-5:]):
            col = SEVERITY_COLOR.get(a["type"], TEXT_GRAY)
            lines.append(
                f'<span style="color:{col}">●</span> '
                f'[{a["date"]} {a["time"]}] '
                f'<b>{a["type"]}</b> — '
                f'{a["cls"]} ID {a["id"]} — {a["details"]}'
            )
        self.recent_label.setText("<br>".join(lines))
        self.recent_label.setTextFormat(Qt.RichText)

    def clear_history(self):
        self.alert_log = []
        self.history_table.setRowCount(0)
        self.count_label.setText("0 alerts")
        self.recent_label.setText("No alerts yet.")

    def open_report(self):
        from ui.report_dialog import ReportDialog

        dlg = ReportDialog(snapshot=self.last_frame_pix, parent=self)
        dlg.exec_()

    def open_amber(self):
        from ui.amber_dialog import AmberDialog

        dlg = AmberDialog(snapshot=self.last_frame_pix, parent=self)
        if dlg.exec_() == dlg.Accepted:
            data = dlg.get_data()
            data["camera"] = "Camera 1 — Main Feed"
            self.amber_engine.activate(data)

    def closeEvent(self, event):
        self.vworker.stop()
        self.vthread.quit()
        self.vthread.wait()
        event.accept()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DashboardWindow()
    w.show()
    sys.exit(app.exec_())