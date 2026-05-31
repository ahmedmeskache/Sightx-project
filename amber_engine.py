import time
import config


class AmberEngine:
    def __init__(self):
        self.is_active = False
        self.case_data = None
        self.matched_track_ids = set()
        self.telegram_client = None

        print(f"[AMBER] TELEGRAM_ENABLED = {config.TELEGRAM_ENABLED}")
        print(f"[AMBER] TOKEN present: {bool(config.TELEGRAM_TOKEN)}")
        print(f"[AMBER] CHAT_IDS: {getattr(config, 'TELEGRAM_CHAT_IDS', [config.TELEGRAM_CHAT_ID])}")

        if config.TELEGRAM_ENABLED and config.TELEGRAM_TOKEN:
            try:
                import telebot
                self.telegram_client = telebot.TeleBot(config.TELEGRAM_TOKEN)
                print("[AMBER] Telegram bot initialized successfully")
            except Exception as e:
                print(f"[AMBER] Telegram bot init failed: {e}")
        else:
            print("[AMBER] Telegram disabled or token missing")

    def activate(self, case_info):
        self.case_data = case_info
        self.is_active = True
        self.matched_track_ids.clear()
        print(f"[AMBER] Alert activated: {case_info['description'][:60]}...")
        self._notify_telegram(
            "🚨 *AMBER ALERT ACTIVATED*\n\n"
            f"*Description:* {case_info['description']}\n"
            f"*Last Seen:* {case_info['location']}\n"
            f"*Contact:* {case_info['contact']}\n"
            f"*Time:* {case_info['timestamp']}\n\n"
            "Live scanning is now active on all cameras."
        )

    def deactivate(self):
        self.is_active = False
        self.case_data = None
        self.matched_track_ids.clear()
        print("[AMBER] Alert deactivated.")

    def scan(self, detection, frame=None):
        if not self.is_active:
            return False
        if detection.get("cls") != 0:
            return False

        track_id = detection.get("track_id")
        if track_id is None:
            return False
        if track_id in self.matched_track_ids:
            return False

        print(f"[AMBER] Scanning person ID {track_id}...")

        self.matched_track_ids.add(track_id)
        print(f"[AMBER] MATCH on ID {track_id}! Sending Telegram...")

        msg = (
            "⚠️ *POTENTIAL MATCH DETECTED*\n\n"
            f"*Missing Child:* {self.case_data['description']}\n"
            f"*Track ID:* #{track_id}\n"
            f"*Camera:* {self.case_data.get('camera', 'Unknown')}\n"
            f"*Time:* {time.strftime('%H:%M:%S')}\n\n"
            f"*Reporter:* {self.case_data['contact']}\n"
            "Please verify immediately."
        )

        self._notify_telegram(msg)

        if frame is not None and config.SNAPSHOT_ENABLED:
            try:
                import cv2
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = f"{config.OUTPUTS_DIR}/AMBER_ID{track_id}_{ts}.jpg"
                cv2.imwrite(path, frame)
                print(f"[AMBER] Snapshot saved: {path}")
            except Exception as e:
                print(f"[AMBER] Snapshot failed: {e}")

        return True

    def _notify_telegram(self, text):
        if self.telegram_client is None:
            print(f"[AMBER] Telegram not configured. Would send:\n{text}")
            return

        chat_ids = getattr(config, 'TELEGRAM_CHAT_IDS', [])
        if not chat_ids and config.TELEGRAM_CHAT_ID:
            chat_ids = [config.TELEGRAM_CHAT_ID]

        print(f"[AMBER] Sending to {len(chat_ids)} chat(s)...")

        for chat_id in chat_ids:
            if not chat_id:
                continue
            try:
                self.telegram_client.send_message(chat_id, text, parse_mode="Markdown")
                print(f"[AMBER] ✅ Telegram sent to {chat_id}")
            except Exception as e:
                print(f"[AMBER] ❌ Telegram failed for {chat_id}: {e}")