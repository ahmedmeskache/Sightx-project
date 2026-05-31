# SightX Project

The SightX Project is a system that watches video feeds in time and tells you when something strange happens. It finds people and cars follows them and points out things like speeding going where you are not supposed to hanging around and running quickly. It also has a special mode called Amber Alert that sends a message on Telegram when someone being watched disappears.

What the SightX Project does

- It finds people and cars in video feeds in time using something called YOLOv8 Nano

- It follows them from one frame to the next and gives them a special ID using BotSort

- It figures out how fast cars are going in kilometers per hour

- It points out things that are not normal: speeding, going into areas that are off limits hanging around and running quickly

- It sends a message on Telegram with a picture when someone disappears, which is called an Amber Alert

- It saves pictures automatically when something strange happens

- It makes reports in PDF format with timestamps, what happened and pictures

- It lets people who use the system make their own reports with pictures and descriptions

- It shows all the things that have happened grouped by date and how serious they are

- It has a simple and easy to use interface with a dark background

How the SightX Project works

1. You plug in a camera. Put a video file in a special folder

2. The system looks at every frame of the video. Uses YOLOv8 and BotSort to follow people and cars

3. It checks each person or car to see if they are doing something

4. If something strange is found it takes a picture makes a sound and writes it down

5. If someone disappears it sends a message on Telegram with a picture

6. The person using the system can look at what has happened make a report or make a report with all the details

The SightX Project uses a few different tools

Python 3.10, PyQt5, OpenCV, YOLOv8, BotSort, ReportLab and the Telegram Bot API

The files in the SightX Project are organized like this:

```

sightX/

├── main.py              This is the file that starts the system

├── config.py            This file has all the settings for the system

├── detector.py          This file uses YOLOv8 to find people and cars

├── tracker.py           This file follows people and cars and checks for behavior

├── alert.py             This file saves pictures and makes sounds when something strange happens

├── report.py            This file makes reports in PDF format

├── ai_engine.py         This file is the brain of the system. Analyzes the video

├── amber_engine.py      This file is used for the Amber Alert system

├── pose_analyzer.py     This file analyzes how people are standing or moving

├── models/              This is where you put the YOLOv8 files

├── videos/              This is where you put your video files

├── outputs/             This is where the system saves pictures and reports

└── ui/

├── login.py         This is the login screen

├── welcome.py       This is the screen

├── dashboard.py     This is the main screen where you can see what is happening

├── history.py       This is where you can see what has happened in the

└── report_dialog.py This is where you can make a report

```

To get the SightX Project working on your computer

```

1- Download the SightX Project from GitHub

2- Go into the SightX Project folder

3- Install the tools you need: torch, torchvision, numpy, ultralytics, PyQt5 opencv-python, reportlab and pyTelegramBotAPI

4- Make folders for models, videos and outputs

5- Put the YOLOv8 files in the models folder

6- Start the system by running the main.py file

```

To change the settings
Edit the config.py file to change the Telegram bot token, chat IDs, speed limit and other settings.

the SightX Project :

Meskache Ahmed and Mezouani Oudai Brahim
Supervised by Dr. Bouslah Ayoub
the University of Badji Mokhtar in Annaba and they worked on the project from 2025, to 2026.
