"""
VisionMag AI - V2 (School Analytics)
--------------------------------------
Upgrades Prototype V1 from a plain object counter into a small school
analytics tool: occupancy %, empty seats, confidence filtering, a CSV
session log, and a proper dashboard overlay.

Controls:
    Q - Quit (prints a session summary first)
    S - Save a screenshot to screenshots/
"""

import os
import time

import cv2
from ultralytics import YOLO

import config
import dashboard
import utils
from logger import SessionLogger


def ensure_dirs():
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)


def draw_detections(frame, boxes, class_names):
    """
    Draw a box + label for every detection in a tracked class above the
    confidence threshold. Returns (counts_per_class, average_confidence_pct).
    """
    counts = {cls_key: 0 for cls_key in config.TRACKED_CLASSES}
    confidences = []

    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = class_names[cls_id]

        if cls_name not in config.TRACKED_CLASSES:
            continue

        confidence = float(box.conf[0])
        if confidence < config.CONFIDENCE_THRESHOLD:
            continue

        counts[cls_name] += 1
        confidences.append(confidence)

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = utils.get_color(cls_name)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"{config.TRACKED_CLASSES[cls_name]} {confidence:.2f}"
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame, (x1, y1 - text_h - 8), (x1 + text_w + 4, y1), color, -1)
        cv2.putText(
            frame, label, (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA,
        )

    avg_confidence_pct = (sum(confidences) / len(confidences) * 100) if confidences else 0
    return counts, avg_confidence_pct


def save_screenshot(frame):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(config.SCREENSHOT_DIR, f"{timestamp}.png")
    cv2.imwrite(filename, frame)
    print(f"[Saved] {filename}")


class SessionStats:
    """Tracks simple running stats for the end-of-session summary."""

    def __init__(self):
        self.frames_processed = 0
        self.persons_history = []
        self.max_chairs = 0

    def update(self, counts):
        self.frames_processed += 1
        self.persons_history.append(counts.get("person", 0))
        self.max_chairs = max(self.max_chairs, counts.get("chair", 0))

    def print_summary(self):
        print("\n--- Session Summary ---")
        print(f"Frames processed : {self.frames_processed}")
        if self.persons_history:
            print(f"Max persons seen : {max(self.persons_history)}")
            print(f"Avg persons seen : {sum(self.persons_history) / len(self.persons_history):.1f}")
        print(f"Max chairs seen  : {self.max_chairs}")
        print("------------------------\n")


def main():
    ensure_dirs()

    print("Loading YOLO model... (first run may download weights)")
    model = YOLO(config.MODEL_NAME)
    class_names = model.names

    print(f"Opening camera index {config.CAMERA_INDEX}...")
    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        print("ERROR: Could not open webcam. Check CAMERA_INDEX or camera permissions.")
        return

    print("Camera opened. Press 'Q' to quit, 'S' to save a screenshot.")

    session_logger = SessionLogger()
    stats = SessionStats()

    prev_time = time.time()
    screenshot_message_time = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame from webcam.")
                break

            results = model(frame, verbose=False)[0]
            counts, avg_confidence = draw_detections(frame, results.boxes, class_names)

            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now

            occupancy = utils.calculate_occupancy(counts.get("person", 0), config.ROOM_CAPACITY)
            empty_seats = utils.calculate_empty_seats(counts.get("chair", 0), counts.get("person", 0))

            dashboard.draw_dashboard(frame, counts, occupancy, empty_seats, avg_confidence, fps)

            if screenshot_message_time is not None:
                still_showing = dashboard.draw_screenshot_message(frame, screenshot_message_time)
                if not still_showing:
                    screenshot_message_time = None

            stats.update(counts)
            session_logger.maybe_log(counts, fps, occupancy)

            cv2.imshow(config.WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("Quitting...")
                break
            elif key == ord("s"):
                save_screenshot(frame)
                screenshot_message_time = time.time()

    finally:
        cap.release()
        cv2.destroyAllWindows()
        stats.print_summary()


if __name__ == "__main__":
    main()
