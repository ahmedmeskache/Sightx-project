class AnomalyEngine:
    def __init__(self):
        self.score_history = {}

    def analyze(self, detection, pose_result=None):
        base_score = 0.0
        reasons = []

        if detection.get("alert"):
            base_score += 0.6
            reasons.append(detection.get("alert_type", "ALERT"))

        if pose_result and pose_result.get("pose_detected"):
            activity = pose_result.get("activity")
            confidence = pose_result.get("confidence", 0)

            if activity == "running" and confidence > 0.7:
                base_score += 0.35
                reasons.append("AI_RUNNING")
            elif activity == "sitting" and detection.get("elapsed", 0) > 300:
                base_score += 0.15
                reasons.append("LONG_SIT")
            elif activity == "unknown" and confidence < 0.4:
                base_score += 0.05
                reasons.append("SUSPICIOUS_POSE")

        track_id = detection.get("track_id")
        if track_id is not None:
            previous_score = self.score_history.get(track_id, 0.0)
            base_score = 0.7 * base_score + 0.3 * previous_score
            self.score_history[track_id] = base_score

        return {
            "anomaly_score": round(min(base_score, 1.0), 2),
            "reasons": reasons,
            "is_anomaly": base_score >= 0.75,
        }