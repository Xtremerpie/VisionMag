"""
VisionMag AI - Dashboard Overlay
-----------------------------------
Draws the semi-transparent info panel on top of the camera feed:
title, per-class counts, occupancy %, empty seats, confidence, FPS,
and current time. Also handles the short-lived "Screenshot Saved"
message.
"""

import time
from datetime import datetime

import cv2

import config
import utils

PANEL_X, PANEL_Y = 10, 10
PANEL_WIDTH = 300
LINE_HEIGHT = 26
TITLE_HEIGHT = 34


def _panel_lines(counts, occupancy, empty_seats, avg_confidence, fps):
    """Build the ordered list of (label, value) rows shown in the panel."""
    lines = []
    for cls_key, label in config.TRACKED_CLASSES.items():
        lines.append((label, str(counts.get(cls_key, 0))))

    lines.append(("Occupancy", f"{occupancy}%"))
    lines.append(("Empty Seats", str(empty_seats)))
    lines.append(("Confidence", f"{avg_confidence:.0f}%"))

    if config.SHOW_FPS:
        lines.append(("FPS", f"{fps:.1f}"))

    lines.append(("Time", datetime.now().strftime("%H:%M:%S")))
    return lines


def draw_dashboard(frame, counts, occupancy, empty_seats, avg_confidence, fps):
    """
    Draw the full VisionMag AI dashboard panel in the top-left corner
    of the frame. Returns nothing; modifies frame in place.
    """
    lines = _panel_lines(counts, occupancy, empty_seats, avg_confidence, fps)
    panel_height = TITLE_HEIGHT + LINE_HEIGHT * len(lines) + 16

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (PANEL_X, PANEL_Y),
        (PANEL_X + PANEL_WIDTH, PANEL_Y + panel_height),
        (0, 0, 0),
        thickness=-1,
    )
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # Title
    cv2.putText(
        frame,
        config.WINDOW_NAME,
        (PANEL_X + 12, PANEL_Y + 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.line(
        frame,
        (PANEL_X + 10, PANEL_Y + TITLE_HEIGHT),
        (PANEL_X + PANEL_WIDTH - 10, PANEL_Y + TITLE_HEIGHT),
        (120, 120, 120),
        1,
    )

    # Rows
    y = PANEL_Y + TITLE_HEIGHT + 24
    for label, value in lines:
        cv2.putText(
            frame,
            f"{label}",
            (PANEL_X + 14, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            value,
            (PANEL_X + PANEL_WIDTH - 90, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        y += LINE_HEIGHT

    return panel_height


def draw_screenshot_message(frame, message_start_time, duration=2.0):
    """
    If a screenshot was saved within the last `duration` seconds, draw a
    "Screenshot Saved" banner near the bottom of the frame.
    Returns True while the message is still being shown, False once expired.
    """
    if message_start_time is None:
        return False

    elapsed = time.time() - message_start_time
    if elapsed > duration:
        return False

    text = "Screenshot Saved"
    frame_h, frame_w = frame.shape[:2]
    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

    x = (frame_w - text_w) // 2
    y = frame_h - 30

    cv2.rectangle(
        frame,
        (x - 12, y - text_h - 10),
        (x + text_w + 12, y + 10),
        (0, 0, 0),
        thickness=-1,
    )
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    return True
