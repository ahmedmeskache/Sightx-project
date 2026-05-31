import math
import time
import config


class Tracker:
    def __init__(self):
        self.last_centers = {}
        self.last_speeds = {}
        self.first_seen_time = {}
        self.last_alert_type = {}
        print("[INFO] Tracker initialized.")

    def _euclidean_distance(self, a, b):
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

    def _is_in_restricted_zone(self, center, track_id):
        if config.RESTRICTED_ZONE is None:
            return False
        cx, cy = center
        x1, y1, x2, y2 = config.RESTRICTED_ZONE
        if x1 < cx < x2 and y1 < cy < y2:
            print(f"[ALERT] Zone intrusion — Person ID {track_id}")
            return True
        return False

    def _is_loitering(self, track_id):
        if track_id not in self.first_seen_time:
            return False
        elapsed = time.time() - self.first_seen_time[track_id]
        if elapsed > config.LOITER_LIMIT_SECONDS:
            print(f"[ALERT] Loitering — Person ID {track_id} in scene for {elapsed:.0f}s")
            return True
        return False

    def _is_running(self, track_id, center, fps):
        if track_id not in self.last_centers:
            return False
        distance = self._euclidean_distance(self.last_centers[track_id], center)
        if distance > config.RUNNING_THRESHOLD:
            print(f"[ALERT] Running detected — Person ID {track_id} (displacement: {distance:.1f}px)")
            return True
        return False

    def update(self, detections, fps):
        for detection in detections:
            track_id = detection.get("track_id")
            class_id = detection["cls"]
            center = detection["center"]

            detection["speed"] = 0.0
            detection["alert"] = False
            detection["alert_type"] = None
            detection["elapsed"] = 0.0

            if track_id is None:
                continue

            if track_id not in self.first_seen_time:
                self.first_seen_time[track_id] = time.time()

            detection["elapsed"] = round(time.time() - self.first_seen_time[track_id], 1)

            if class_id == 2:
                if track_id in self.last_centers:
                    distance = self._euclidean_distance(self.last_centers[track_id], center)
                    speed = distance * fps * config.SCALE_FACTOR
                    self.last_speeds[track_id] = speed
                    detection["speed"] = round(speed, 1)
                    if speed > config.SPEED_LIMIT:
                        detection["alert"] = True
                        detection["alert_type"] = "SPEED"

            elif class_id == 0:
                if self._is_in_restricted_zone(center, track_id):
                    detection["alert"] = True
                    detection["alert_type"] = "ZONE"
                elif self._is_running(track_id, center, fps):
                    detection["alert"] = True
                    detection["alert_type"] = "RUNNING"
                elif self._is_loitering(track_id):
                    detection["alert"] = True
                    detection["alert_type"] = "LOITER"

            self.last_centers[track_id] = center

        return detections

    def get_speed(self, track_id):
        return self.last_speeds.get(track_id, 0.0)

    def cleanup(self, active_ids):
        for track_id in list(self.last_centers.keys()):
            if track_id not in active_ids:
                self.last_centers.pop(track_id, None)
                self.last_speeds.pop(track_id, None)
                self.first_seen_time.pop(track_id, None)
                self.last_alert_type.pop(track_id, None)