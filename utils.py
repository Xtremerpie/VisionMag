"""
VisionMag AI - Utilities
--------------------------
Small, dependency-free helper functions used across the app:
box colors and the two core "school analytics" calculations
(occupancy % and empty seats).
"""

# Bounding box colors per class, in BGR (OpenCV format).
BOX_COLORS = {
    "person": (0, 200, 0),     # green
    "chair": (255, 140, 0),    # blue-ish
    "backpack": (0, 165, 255), # orange
    "book": (200, 0, 160),     # purple
}
DEFAULT_COLOR = (200, 200, 200)


def get_color(class_name):
    """Return the display color for a tracked class name."""
    return BOX_COLORS.get(class_name, DEFAULT_COLOR)


def calculate_occupancy(persons, room_capacity):
    """
    Occupancy % = detected persons / room capacity, clamped to 0-100.
    Returns 0 if room_capacity is 0 or invalid, to avoid a divide-by-zero.
    """
    if not room_capacity or room_capacity <= 0:
        return 0
    occupancy = (persons / room_capacity) * 100
    return max(0, min(100, round(occupancy)))


def occupancy_status(occupancy_percent):
    """
    Simple status label for a given occupancy percentage.
    Thresholds are intentionally simple for V2; can be refined later
    with real classroom data.
    """
    if occupancy_percent >= 90:
        return "FULL"
    if occupancy_percent >= 70:
        return "BUSY"
    if occupancy_percent >= 30:
        return "NORMAL"
    return "LOW"


def calculate_empty_seats(chairs, persons):
    """
    Empty seats = chairs - persons, never negative
    (e.g. if people are standing/not in the frame's chair count).
    """
    return max(0, chairs - persons)
