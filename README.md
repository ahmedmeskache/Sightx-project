# SightX

SightX is a real-time AI surveillance system that monitors video feeds and alerts you when something suspicious happens. It detects people and vehicles, tracks their movements, and flags behaviours like speeding, trespassing, loitering, and sudden running. It also includes an Amber Alert mode that sends instant Telegram notifications when a tracked person goes missing.

---

## What it does

- Detects people and vehicles in real time using YOLOv8 Nano
- Tracks them across frames with persistent IDs using BotSort
- Estimates vehicle speed in km/h from pixel displacement
- Flags anomalies: speed violations, restricted zone intrusions, loitering, sudden running
- Sends instant Telegram alerts with snapshot evidence when a person disappears (Amber Alert)
- Saves JPEG snapshots automatically for every alert to the outputs/ folder
- Generates PDF incident reports with timestamps, alert breakdowns, and evidence photos
- Lets operators file manual incident reports with scene capture, plate photo, suspect photo, and written description
- Displays full detection history grouped by date and classified by severity
- Clean dark-theme desktop interface: animated welcome screen, live camera dashboard, history browser

---

## How it works

1. Plug in a camera or place a video file in the videos/ folder
2. The detection engine runs YOLOv8 on every frame and assigns track IDs via BotSort
3. The tracker scores each object for speed violations and behavioural anomalies
4. When an anomaly is detected, the system captures a snapshot, plays a sound alert, and logs the event
5. For Amber Alerts, a Telegram notification with the evidence photo is dispatched immediately
6. The operator can browse history, file a manual report, or generate a full PDF forensic report

---

## Tech stack

Python 3.10, PyQt5, OpenCV, YOLOv8, BotSort, ReportLab, Telegram Bot API

---

## Project structure

```
sightX/
├── main.py              Entry point — connects all screens
├── config.py            Central configuration
├── detector.py          YOLOv8 detection, BotSort tracking, frame annotation
├── tracker.py           Speed estimation and behaviour detection
├── alert.py             Snapshot saving, sound, cooldown, alert log
├── report.py            PDF report generator
├── ai_engine.py         AI analysis engine
├── amber_engine.py      Amber Alert — missing person detection and Telegram
├── pose_analyzer.py     Human pose estimation
├── models/              Place yolov8n.pt here
├── videos/              Place your .mp4 or .avi files here
├── outputs/             Auto-created — snapshots, logs, and reports saved here
└── ui/
    ├── login.py         Login screen (Employee ID + Company Code)
    ├── welcome.py       Welcome screen with animated sphere and two action buttons
    ├── dashboard.py     Live camera feed, stat cards, alert history
    ├── history.py       Detection history grouped by date and severity
    └── report_dialog.py Paper-style manual incident report form
```

---

## Install

```bash
git clone https://github.com/ahmedmeskache/Sightx-project.git
cd Sightx-project
```

```bash
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu
pip install numpy==1.26.4
pip install ultralytics PyQt5 opencv-python reportlab requests pyTelegramBotAPI
```

```bash
mkdir models videos outputs
```

Place `yolov8n.pt` in the `models/` folder, or let it download automatically on first run.

---

## Run

```bash
python main.py
```

---

## Config

Edit `config.py` to set your Telegram bot token, chat IDs, speed limit, restricted zone coordinates, loitering timeout, and file paths.

---

## Authors

Meskache Ahmed and Mezouani Oudai Brahim

Supervised by Dr. Bouslah Ayoub

University of Badji Mokhtar — Annaba, 2025–2026
