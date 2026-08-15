"""
VisionMag AI - Configuration
-----------------------------
Central place to tune the app without touching the detection code.
Edit these values and re-run main.py.
"""

# --- Camera / Model ---------------------------------------------------
CAMERA_INDEX = 0
MODEL_NAME = "yolov8n.pt"

# --- Detection ----------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.5

# Classes we track, mapped to display labels.
# (Matches Ultralytics/COCO class names on the left.)
TRACKED_CLASSES = {
    "person": "Persons",
    "chair": "Chairs",
    "backpack": "Bags",
    "book": "Books",
}

# --- School Analytics -----------------------------------------------------
ROOM_CAPACITY = 40  # used to calculate Occupancy %

# --- Dashboard ------------------------------------------------------------
WINDOW_NAME = "VisionMag AI"
SHOW_FPS = True

# --- Logging / Screenshots -------------------------------------------------
SAVE_LOGS = True
SAVE_SCREENSHOTS = True

LOG_DIR = "logs"
LOG_FILENAME = "session.csv"
LOG_INTERVAL_SECONDS = 1.0  # write one row per second, not every frame

SCREENSHOT_DIR = "screenshots"
