"""
VisionMag AI - CSV Logger
----------------------------
Writes one row per second to logs/session.csv with a timestamp and
the current detection/analytics snapshot. Creates the logs/ folder
and the CSV header automatically if they don't exist yet.
"""

import csv
import os
import time
from datetime import datetime

import config

FIELDNAMES = ["timestamp", "persons", "chairs", "bags", "books", "fps", "occupancy"]


class SessionLogger:
    """
    Call `maybe_log(...)` once per frame; it internally throttles itself
    to write at most once every config.LOG_INTERVAL_SECONDS.
    """

    def __init__(self):
        self.enabled = config.SAVE_LOGS
        self._last_write = 0.0
        self.log_path = os.path.join(config.LOG_DIR, config.LOG_FILENAME)

        if self.enabled:
            self._ensure_file()

    def _ensure_file(self):
        os.makedirs(config.LOG_DIR, exist_ok=True)
        file_exists = os.path.isfile(self.log_path)
        if not file_exists:
            with open(self.log_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def maybe_log(self, counts, fps, occupancy):
        """
        Write a row if enough time has passed since the last write.
        Silently does nothing if logging is disabled in config.py.
        """
        if not self.enabled:
            return

        now = time.time()
        if now - self._last_write < config.LOG_INTERVAL_SECONDS:
            return

        self._last_write = now
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "persons": counts.get("person", 0),
            "chairs": counts.get("chair", 0),
            "bags": counts.get("backpack", 0),
            "books": counts.get("book", 0),
            "fps": round(fps, 1),
            "occupancy": occupancy,
        }

        with open(self.log_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)
