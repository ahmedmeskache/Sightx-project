import cv2
import numpy as np
import math
import time

_MP_AVAILABLE = False
mp_pose = None
mp_drawing = None

try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as _mp_pose_module
    mp_pose = _mp_pose_module
    mp_drawing = mp.python.solutions.drawing_utils
    _MP_AVAILABLE = True
    print("[INFO] MediaPipe loaded successfully.")
except Exception as e:
    print(f"[WARN] MediaPipe not available: {e}")
    print("[WARN] Pose detection disabled. Run:  python -m pip install mediapipe==0.10.35")


class PoseAnalyzer:
    def __init__(self):
        if not _MP_AVAILABLE:
            print("[INFO] PoseAnalyzer in PASS-THROUGH mode.")
            self.pose = None
            self.activity_history = {}
            self.movement_tracks = {}
            return

        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.activity_history = {}
        self.history_size = 10
        self.movement_tracks = {}
        print("[INFO] AI Pose Analyzer initialized (MediaPipe)")

    def analyze_person(self, frame, bbox):
        if not _MP_AVAILABLE or self.pose is None:
            return self._no_pose_result()

        x1, y1, x2, y2 = bbox
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return self._no_pose_result()

        pad = 10
        px1, py1 = max(0, x1 - pad), max(0, y1 - pad)
        px2, py2 = min(w, x2 + pad), min(h, y2 + pad)
        person_crop = frame[py1:py2, px1:px2]

        if person_crop.size == 0:
            return self._no_pose_result()

        rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if not results.pose_landmarks:
            return self._no_pose_result()

        landmarks = results.pose_landmarks.landmark
        ankle_score = self._ankle_activity_score(landmarks)
        knee_score = self._knee_bend_score(landmarks)
        activity, confidence = self._determine_activity(ankle_score, knee_score, landmarks)

        keypoints = {}
        for idx, lm in enumerate(landmarks):
            keypoints[idx] = (
                int(lm.x * (px2 - px1)) + px1,
                int(lm.y * (py2 - py1)) + py1,
                lm.visibility
            )

        return {
            "pose_detected": True,
            "activity": activity,
            "confidence": round(confidence, 2),
            "keypoints": keypoints,
            "is_stationary": ankle_score < 0.15,
            "movement_score": round(ankle_score, 2),
            "knee_bend": round(knee_score, 2)
        }

    def _ankle_activity_score(self, landmarks):
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        ankle_diff = abs(left_ankle.y - right_ankle.y)
        vertical_movement = max(left_ankle.y, right_ankle.y) - min(left_ankle.y, right_ankle.y)
        activity_score = (ankle_diff * 2 + vertical_movement) / 2
        return min(activity_score * 3, 1.0)

    def _knee_bend_score(self, landmarks):
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        hip_ankle_avg = (left_hip.y + left_ankle.y) / 2
        knee_drop = abs(left_knee.y - hip_ankle_avg)
        return min(knee_drop * 5, 1.0)

    def _determine_activity(self, ankle_score, knee_score, landmarks):
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        is_sitting = left_hip.y > left_knee.y and knee_score > 0.6
        if is_sitting:
            return "sitting", 0.85
        if ankle_score > 0.4 and knee_score > 0.3:
            return "running", min(ankle_score * 1.5, 1.0)
        elif ankle_score > 0.15 and knee_score > 0.1:
            return "walking", min(ankle_score * 2, 1.0)
        elif ankle_score < 0.1 and knee_score < 0.15:
            return "standing", 0.9
        else:
            return "unknown", 0.5

    def _no_pose_result(self):
        return {
            "pose_detected": False,
            "activity": "unknown",
            "confidence": 0.0,
            "keypoints": {},
            "is_stationary": False,
            "movement_score": 0.0,
            "knee_bend": 0.0
        }

    def update_activity_history(self, track_id, activity, confidence):
        if track_id not in self.activity_history:
            self.activity_history[track_id] = []
        self.activity_history[track_id].append((activity, confidence))
        if len(self.activity_history[track_id]) > self.history_size:
            self.activity_history[track_id].pop(0)
        activities = [a for a, c in self.activity_history[track_id]]
        from collections import Counter
        counts = Counter(activities)
        most_common = counts.most_common(1)[0][0]
        avg_conf = sum(c for a, c in self.activity_history[track_id] if a == most_common)
        avg_conf /= counts[most_common]
        return most_common, round(avg_conf, 2)

    def track_movement(self, track_id, center, timestamp):
        if track_id not in self.movement_tracks:
            self.movement_tracks[track_id] = {"positions": [], "total_distance": 0.0}
        track = self.movement_tracks[track_id]
        track["positions"].append((center[0], center[1], timestamp))
        cutoff = timestamp - 30
        track["positions"] = [p for p in track["positions"] if p[2] > cutoff]
        if len(track["positions"]) > 1:
            total = 0.0
            for i in range(1, len(track["positions"])):
                dx = track["positions"][i][0] - track["positions"][i-1][0]
                dy = track["positions"][i][1] - track["positions"][i-1][1]
                total += math.sqrt(dx*dx + dy*dy)
            track["total_distance"] = total
        return track["total_distance"]

    def get_stationary_score(self, track_id):
        if track_id not in self.movement_tracks:
            return 0.0
        total_dist = self.movement_tracks[track_id]["total_distance"]
        if total_dist < 50:
            return 1.0
        elif total_dist < 150:
            return 0.5
        return 0.0

    def cleanup(self, active_ids):
        for tid in list(self.activity_history.keys()):
            if tid not in active_ids:
                self.activity_history.pop(tid, None)
                self.movement_tracks.pop(tid, None)

    def draw_pose(self, frame, keypoints, activity):
        if not _MP_AVAILABLE or not keypoints:
            return frame

        colors = {
            "standing": (255, 0, 255),
            "walking": (0, 255, 255),
            "running": (0, 165, 255),
            "sitting": (0, 255, 0),
            "unknown": (128, 128, 128)
        }
        color = colors.get(activity, (255, 255, 255))

        for idx, (x, y, vis) in keypoints.items():
            if vis > 0.5:
                cv2.circle(frame, (x, y), 3, color, -1)

        if 0 in keypoints:
            x, y, _ = keypoints[0]
            label = f"{activity.upper()}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x - tw//2 - 2, y - 25), (x + tw//2 + 6, y - 5), (0, 0, 0), -1)
            cv2.putText(frame, label, (x - tw//2 + 2, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return frame