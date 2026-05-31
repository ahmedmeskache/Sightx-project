import cv2
import config
from ultralytics import YOLO


class Detector:
    def __init__(self):
        print(f"[INFO] Loading model from: {config.MODEL_PATH}")
        try:
            self.model = YOLO(config.MODEL_PATH)
            print("[INFO] Model loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise

    def detect(self, frame):
        try:
            results = self.model.track(
                frame,
                persist=True,
                verbose=False,
                conf=config.CONFIDENCE_THRESHOLD,
                iou=0.5,
                imgsz=320,
                tracker="botsort.yaml",
                device='cpu',
                half=False,
            )
        except Exception as e:
            print(f"[WARNING] Tracking failed: {e}")
            try:
                results = self.model(
                    frame,
                    verbose=False,
                    conf=config.CONFIDENCE_THRESHOLD,
                    iou=0.5,
                    imgsz=320,
                )
            except Exception as e2:
                print(f"[WARNING] Detection also failed: {e2}")
                return []

        detection_list = []

        if results is None or len(results) == 0:
            return detection_list
        if results[0].boxes is None:
            return detection_list

        boxes = results[0].boxes

        for index, box in enumerate(boxes):
            try:
                class_id = int(box.cls[0])
                if class_id not in config.ALLOWED_CLASSES:
                    continue

                confidence = float(box.conf[0])
                track_id = None
                if boxes.id is not None:
                    track_id = int(boxes.id[index].item())

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                detection_list.append({
                    "bbox": (x1, y1, x2, y2),
                    "cls": class_id,
                    "label": config.CLASS_NAMES[class_id],
                    "conf": confidence,
                    "center": (cx, cy),
                    "track_id": track_id,
                    "speed": 0.0,
                    "alert": False,
                    "alert_type": None,
                    "elapsed": 0.0,
                })

            except Exception as e:
                print(f"[WARNING] Skipping box: {e}")
                continue

        return detection_list

    def draw(self, frame, detection_list):
        frame_out = frame.copy()

        if config.RESTRICTED_ZONE:
            zx1, zy1, zx2, zy2 = config.RESTRICTED_ZONE
            overlay = frame_out.copy()
            cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), config.COLOR_ZONE, -1)
            cv2.addWeighted(overlay, 0.2, frame_out, 0.8, 0, frame_out)
            cv2.rectangle(frame_out, (zx1, zy1), (zx2, zy2), config.COLOR_ZONE, 2)
            cv2.putText(frame_out, "RESTRICTED", (zx1, zy1 - 8),
                        config.FONT, 0.5, config.COLOR_ZONE, 1)

        for det in detection_list:
            x1, y1, x2, y2 = det["bbox"]
            alert_type = det.get("alert_type")

            if not det.get("alert"):
                color = config.COLOR_NORMAL
            elif alert_type == "ZONE":
                color = (0, 0, 255)
            elif alert_type == "RUNNING":
                color = (0, 165, 255)
            elif alert_type == "LOITER":
                color = (0, 255, 255)
            elif alert_type == "SPEED":
                color = (0, 0, 255)
            else:
                color = config.COLOR_ALERT

            tid = det.get("track_id")
            id_label = f"ID {tid}" if tid is not None else "ID ?"

            if det["cls"] == 2:
                speed = det.get("speed", 0.0)
                violation_marker = " ⚠" if det.get("alert") else ""
                label = f"Car {id_label} | {speed:.1f} km/h{violation_marker}"
            else:
                elapsed = det.get("elapsed", 0.0)
                if alert_type == "ZONE":
                    label = f"Person {id_label} | ZONE INTRUSION ⚠"
                elif alert_type == "RUNNING":
                    label = f"Person {id_label} | RUNNING ⚠"
                elif alert_type == "LOITER":
                    label = f"Person {id_label} | LOITERING {elapsed:.0f}s ⚠"
                else:
                    label = f"Person {id_label} | {elapsed:.0f}s"

            cv2.rectangle(frame_out, (x1, y1), (x2, y2), color, config.BOX_THICKNESS)

            (tw, th), _ = cv2.getTextSize(label, config.FONT, config.FONT_SCALE, config.FONT_THICKNESS)
            cv2.rectangle(frame_out, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(frame_out, label, (x1 + 2, y1 - 5), config.FONT, config.FONT_SCALE, (0, 0, 0), config.FONT_THICKNESS)

            cv2.circle(frame_out, det["center"], 4, color, -1)

        return frame_out