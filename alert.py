import cv2
import os
import time
import config


class AlertSystem:
    def __init__(self):
        os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
        self.alert_log = []
        self.cooldown_map = {}
        self.cooldown_seconds = 5
        print("[INFO] Alert system initialized.")
        print(f"[INFO] Snapshots will be saved to: {config.OUTPUTS_DIR}")

    def is_on_cooldown(self, track_id):
        if track_id not in self.cooldown_map:
            return False
        return (time.time() - self.cooldown_map[track_id]) < self.cooldown_seconds

    def set_cooldown(self, track_id):
        self.cooldown_map[track_id] = time.time()

    def save_snapshot(self, frame, alert_type, track_id, detection=None):
        if not config.SNAPSHOT_ENABLED:
            return None, None

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        out_dir = config.OUTPUTS_DIR

        full_name = f"{alert_type}_ID{track_id}_{timestamp}.jpg"
        full_path = os.path.join(out_dir, full_name)
        cv2.imwrite(full_path, frame)
        print(f"[SAVED] Full snapshot: {full_path}")

        crop_path = None
        if detection and "bbox" in detection:
            x1, y1, x2, y2 = detection["bbox"]
            pad = 20
            h, w = frame.shape[:2]
            cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
            cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)

            crop = frame[cy1:cy2, cx1:cx2].copy()

            cv2.rectangle(crop, (pad, pad), (crop.shape[1] - pad, crop.shape[0] - pad), (0, 0, 255), 3)

            label = f"ID {track_id} | {alert_type}"
            cv2.putText(crop, label, (pad, pad - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            crop_name = f"{alert_type}_ID{track_id}_{timestamp}_CROP.jpg"
            crop_path = os.path.join(out_dir, crop_name)
            cv2.imwrite(crop_path, crop)
            print(f"[SAVED] Offender crop: {crop_path}")

        return full_path, crop_path

    def play_sound(self):
        if not config.SOUND_ALERT:
            return
        try:
            import winsound
            winsound.Beep(1500, 300)
            winsound.Beep(800, 200)
        except ImportError:
            print("\a")

    def log_alert(self, alert_type, track_id, details=""):
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": alert_type,
            "track_id": track_id,
            "details": details,
        }
        self.alert_log.append(entry)
        return entry

    def save_log(self):
        if not self.alert_log:
            print("[INFO] No alerts to log.")
            return
        path = os.path.join(config.OUTPUTS_DIR, "alert_log.txt")
        with open(path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("  SIGHTX ALERT LOG\n")
            f.write("=" * 60 + "\n\n")
            for entry in self.alert_log:
                f.write(
                    f"[{entry['time']}] "
                    f"{entry['type']:<10} "
                    f"ID {entry['track_id']:<4} "
                    f"{entry['details']}\n"
                )
            f.write(f"\nTotal alerts: {len(self.alert_log)}\n")
        print(f"[INFO] Alert log saved to: {path}")

    def trigger(self, frame, detection):
        track_id = detection.get("track_id")
        alert_type = detection.get("alert_type", "UNKNOWN")
        speed = detection.get("speed", 0.0)
        elapsed = detection.get("elapsed", 0.0)

        if track_id is not None and self.is_on_cooldown(track_id):
            return None

        if alert_type == "SPEED":
            details = f"Speed: {speed:.1f} km/h"
        elif alert_type == "LOITER":
            details = f"In scene: {elapsed:.0f}s"
        elif alert_type == "ZONE":
            details = "Entered restricted zone"
        elif alert_type == "RUNNING":
            details = "Sudden movement detected"
        else:
            details = ""

        self.save_snapshot(frame, alert_type, track_id, detection)
        self.play_sound()
        entry = self.log_alert(alert_type, track_id, details)

        if track_id is not None:
            self.set_cooldown(track_id)

        return entry