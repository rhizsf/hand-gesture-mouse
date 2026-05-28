# Hand Gesture Mouse Controller

An AI-powered computer vision application that allows you to control your laptop's mouse cursor using hand gestures captured through your webcam. Built with Python, OpenCV, and Google MediaPipe.

---

## Features

- **Real-Time Hand Tracking**: Detects and tracks hand landmarks with low latency using Google MediaPipe Hands.
- **Cursor Movement**: Move the cursor smoothly across the screen by moving your index finger.
- **Left Click**: Perform a left click by bringing your index finger and thumb close together (or an alternative pinch gesture).
- **Right Click**: Perform a right click by bringing your middle finger and thumb close together.
- **Security & Privacy**: Standard configuration templates to prevent leaking personal information, absolute directory paths, or local IP addresses when pushing code to GitHub.

---

## Directory Structure

```text
handgesture mouse/
│
├── src/
│   ├── __init__.py
│   ├── hand_tracker.py       # Manages webcam feed and detects hand landmarks
│   └── mouse_driver.py       # Simulates mouse movements, clicks, and smoothing
│
├── .env.example              # Environment variables template (safe to commit)
├── .env                      # Local settings file (ignored by Git, never committed)
├── .gitignore                # Ensures environment variables and caches stay local
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point orchestrating webcam and mouse control
└── README.md                 # Project documentation
```

---

## Security (GitHub Best Practices)

To ensure that your local development settings (such as camera index, custom mouse sensitivities, or local server IP addresses for future mobile connections) are never committed to GitHub, the project uses a `.gitignore` configuration.

Your local `.env` file contains specific configurations and is automatically ignored by Git. If you add database credentials, private API keys, or networking credentials in the future, they will remain safe.

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher.
- A functional webcam.

### 1. Clone and Navigate
```bash
git clone <your-repository-url>
cd "handgesture mouse"
```

### 2. Create a Virtual Environment
It is highly recommended to isolate your dependencies using a virtual environment:
```bash
# On Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Local Environment File
Copy the configuration template to create your local `.env` file:
```bash
cp .env.example .env
```
*(On Windows cmd/powershell, you can also manually copy `.env.example` and rename it to `.env`).*

You can modify `.env` to adjust cursor sensitivity, smooth out jitter, or change the camera input index.

---

## Running the Application

Activate your virtual environment and run the main entry point:
```bash
python main.py
```

### Basic Gestures (Default)
- **Cursor Movement**: Move your **Index Finger**. The cursor will track its position.
- **Left Click**: Pinch your **Index Finger** and **Thumb** together.
- **Right Click**: Pinch your **Middle Finger** and **Thumb** together.
- **Exit**: Press **`q`** on your keyboard while focusing on the camera window to terminate the application.

---

## Future Android Integration (Local Network)

Once the local laptop hand gesture tracking is stable, an Android extension can be introduced:
1. **Laptop Server**: The laptop runs a WebSocket or TCP Socket server.
2. **Android Client**: An Android app connects to the laptop over the local Wi-Fi network and either transmits camera frames for remote processing or functions as a remote touch controller to trigger PyAutoGUI actions.
