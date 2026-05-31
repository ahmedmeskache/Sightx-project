import sys, os, math, random, time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient,
    QFont, QPainterPath
)

BACKGROUND_COLOR = "#09090b"
ACCENT_COLOR = "#c8ff00"
TEXT_COLOR = "#ffffff"
SECONDARY_TEXT_COLOR = "#888899"
MUTED_TEXT_COLOR = "#333344"
BORDER_COLOR = "#1c1c22"


class SphereWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setMinimumSize(520, 520)
        self.rotation_angle = 0.0
        self.vertex_points = [(
            math.sin(random.uniform(0, math.pi)) * math.cos(random.uniform(0, 2 * math.pi)),
            math.sin(random.uniform(0, math.pi)) * math.sin(random.uniform(0, 2 * math.pi)),
            math.cos(random.uniform(0, math.pi))
        ) for _ in range(200)]
        animation_timer = QTimer(self)
        animation_timer.timeout.connect(self._update_animation)
        animation_timer.start(16)

    def _update_animation(self):
        self.rotation_angle += 0.004
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.40

        glow_gradient = QRadialGradient(center_x, center_y, radius * 1.3)
        glow_gradient.setColorAt(0, QColor(180, 255, 0, 28))
        glow_gradient.setColorAt(0.6, QColor(80, 200, 0, 8))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QRectF(center_x - radius * 1.5, center_y - radius * 1.5, radius * 3, radius * 3))

        projected_points = []
        for x, y, z in self.vertex_points:
            rotated_x = x * math.cos(self.rotation_angle) - z * math.sin(self.rotation_angle)
            rotated_z = x * math.sin(self.rotation_angle) + z * math.cos(self.rotation_angle)
            scale = (rotated_z + 2.2) / 3.2
            projected_points.append((center_x + rotated_x * radius * scale, center_y + y * radius * scale, rotated_z, scale))

        for first_index in range(len(projected_points)):
            for second_index in range(first_index + 1, len(projected_points)):
                x1, y1, z1, _ = projected_points[first_index]
                x2, y2, z2, _ = projected_points[second_index]
                distance = math.hypot(x1 - x2, y1 - y2)
                if distance < radius * 0.42:
                    alpha = int(38 * (1 - distance / (radius * 0.42)))
                    if z1 > 0 and z2 > 0:
                        alpha = min(alpha * 2, 55)
                    painter.setPen(QPen(QColor(200, 255, 0, alpha), 0.7))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        painter.setPen(Qt.NoPen)
        for px, py, depth, scale in projected_points:
            alpha = int(220 * scale) if depth > 0 else 30
            diameter = scale * 4.5 if depth > 0 else scale * 2.0
            painter.setBrush(QBrush(QColor(200, 255, 0, min(255, alpha))))
            painter.drawEllipse(QPointF(px, py), diameter / 2, diameter / 2)

        painter.setPen(QPen(QColor(200, 255, 0, 16), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))
        painter.end()


class LogoWidget(QWidget):
    def __init__(self, size=36, parent=None):
        super().__init__(parent)
        self.symbol_size = size
        self.setFixedSize(size + 118, size + 6)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        size = self.symbol_size
        center_x = size // 2
        center_y = self.height() // 2

        path = QPainterPath()
        for index in range(6):
            angle = math.radians(60 * index - 30)
            x = center_x + size * 0.46 * math.cos(angle)
            y = center_y + size * 0.46 * math.sin(angle)
            if index == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.setPen(QPen(QColor(ACCENT_COLOR), 1.8))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.setPen(QPen(QColor(ACCENT_COLOR), 1.1))
        eye_radius = size * 0.18
        painter.drawEllipse(QPointF(center_x, center_y), eye_radius, eye_radius * 0.65)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(ACCENT_COLOR)))
        painter.drawEllipse(QPointF(center_x, center_y), eye_radius * 0.38, eye_radius * 0.38)

        painter.setPen(QColor(TEXT_COLOR))
        font = QFont("Courier New", size // 3 + 1, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 3.5)
        painter.setFont(font)
        painter.drawText(size + 10, center_y + size // 5 + 3, "SIGHTX")
        painter.end()


class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(54)
        self.setMinimumWidth(215)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style(False)

    def _update_style(self, hovered):
        self.setStyleSheet(f"""QPushButton {{
            background: {"#d4ff1a" if hovered else ACCENT_COLOR};
            color: #000000;
            border: none;
            border-radius: 27px;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 0 28px;
            font-family: 'Courier New';
        }}""")

    def enterEvent(self, event):
        self._update_style(True)

    def leaveEvent(self, event):
        self._update_style(False)


class SecondaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(54)
        self.setMinimumWidth(215)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style(False)

    def _update_style(self, hovered):
        self.setStyleSheet(f"""QPushButton {{
            background: {"rgba(200,255,0,0.07)" if hovered else "transparent"};
            color: {TEXT_COLOR};
            border: 1px solid {"rgba(200,255,0,0.50)" if hovered else "#333344"};
            border-radius: 27px;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 0 28px;
            font-family: 'Courier New';
        }}""")

    def enterEvent(self, event):
        self._update_style(True)

    def leaveEvent(self, event):
        self._update_style(False)


class WelcomeWindow(QMainWindow):
    sig_camera = pyqtSignal()
    sig_history = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SightX Security System")
        self.setMinimumSize(1280, 760)
        self.setStyleSheet(f"background: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        self._build_ui()

    def _build_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QWidget()
        left_panel.setStyleSheet(f"background: {BACKGROUND_COLOR};")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(72, 0, 48, 56)
        left_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setFixedHeight(76)
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(LogoWidget(36))
        header_layout.addStretch()
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(
            f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px; font-family: 'Courier New';")
        header_layout.addWidget(self.clock_label)
        left_layout.addWidget(header_widget)

        left_layout.addStretch(2)

        greeting_label = QLabel("WELCOME, SIR.")
        greeting_label.setStyleSheet(
            f"color: {SECONDARY_TEXT_COLOR}; font-size: 12px; "
            f"letter-spacing: 5px; font-family: 'Courier New';")
        left_layout.addWidget(greeting_label)
        left_layout.addSpacing(18)

        headline_label = QLabel("Intelligent\nSurveillance\nSystem.")
        headline_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 56px; font-weight: 900; line-height: 1.05;")
        left_layout.addWidget(headline_label)
        left_layout.addSpacing(22)

        subtitle_label = QLabel(
            "Real-time detection  ·  Behavioural analysis\n"
            "Speed monitoring  ·  Automated alert reporting")
        subtitle_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR}; font-size: 14px; line-height: 1.7;")
        left_layout.addWidget(subtitle_label)
        left_layout.addSpacing(50)

        button_row = QHBoxLayout()
        button_row.setSpacing(16)
        self.camera_button = PrimaryButton("⬡  Access Camera")
        self.history_button = SecondaryButton("◷  View History")
        self.camera_button.clicked.connect(self.sig_camera.emit)
        self.history_button.clicked.connect(self.sig_history.emit)
        button_row.addWidget(self.camera_button)
        button_row.addWidget(self.history_button)
        button_row.addStretch()
        left_layout.addLayout(button_row)
        left_layout.addSpacing(52)

        status_row = QHBoxLayout()
        status_row.setSpacing(36)
        for label_text, value_text, color_value in [
            ("SYSTEM", "ONLINE", ACCENT_COLOR),
            ("CAMERAS", "ACTIVE", ACCENT_COLOR),
            ("ALERTS", "MONITORING", "#00aaff"),
        ]:
            column_layout = QVBoxLayout()
            column_layout.setSpacing(4)
            value_label = QLabel(value_text)
            value_label.setStyleSheet(
                f"color: {color_value}; font-size: 11px; font-weight: bold; "
                f"letter-spacing: 2px; font-family: 'Courier New';")
            title_label = QLabel(label_text)
            title_label.setStyleSheet(
                f"color: {MUTED_TEXT_COLOR}; font-size: 10px; "
                f"letter-spacing: 2px; font-family: 'Courier New';")
            column_layout.addWidget(value_label)
            column_layout.addWidget(title_label)
            status_row.addLayout(column_layout)
        status_row.addStretch()
        left_layout.addLayout(status_row)
        left_layout.addStretch(1)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"color: {BORDER_COLOR};")

        right_panel = QWidget()
        right_panel.setStyleSheet(f"background: {BACKGROUND_COLOR};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.sphere_widget = SphereWidget()
        right_layout.addWidget(self.sphere_widget, alignment=Qt.AlignCenter)

        main_layout.addWidget(left_panel, stretch=5)
        main_layout.addWidget(divider)
        main_layout.addWidget(right_panel, stretch=5)

        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._refresh_clock)
        clock_timer.start(1000)
        self._refresh_clock()

    def _refresh_clock(self):
        self.clock_label.setText(time.strftime("%A %d %b  ·  %H:%M:%S"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())