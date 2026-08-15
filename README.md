# VisionMag AI — V2 (School Analytics)

Started as Prototype V1 (a plain object counter). V2 turns it into a
small **school analytics** tool: it still detects people, chairs, and
bags (now also books) from a webcam, but adds occupancy %, empty-seat
counting, a proper dashboard overlay, and a CSV session log — so it
answers "what does this mean for the room?" instead of just "what's
visible?"

## Project Structure

```
VisionGuardAI/
├── main.py            # app entry point / camera loop
├── config.py           # all tunable settings in one place
├── dashboard.py         # draws the on-screen analytics panel
├── logger.py            # writes logs/session.csv once per second
├── utils.py              # box colors + occupancy/empty-seat math
├── requirements.txt
├── README.md
├── logs/                # session.csv created here at runtime
├── output/              # reserved for future exports/reports
└── screenshots/          # screenshots saved during testing (press 'S')
```

## What's new in V2

- **Dashboard overlay** — Persons, Chairs, Bags, Books, Occupancy %,
  Empty Seats, average detection Confidence, FPS, and clock, all in one
  panel (`dashboard.py`).
- **Occupancy %** — `persons / ROOM_CAPACITY`, clamped 0–100 (`utils.py`).
- **Empty seats** — `chairs - persons`, never negative (`utils.py`).
- **Confidence filtering** — detections below `CONFIDENCE_THRESHOLD`
  (default `0.5`) are ignored, to cut down false positives.
- **CSV logging** — one row per second to `logs/session.csv`
  (timestamp, persons, chairs, bags, books, fps, occupancy) — ready to
  drop into a spreadsheet for graphs in your NCSC report (`logger.py`).
- **Screenshot feedback** — pressing `S` now shows an on-screen
  "Screenshot Saved" banner for 2 seconds.
- **Session summary** — printed to the console when you quit: frames
  processed, max/average persons seen, max chairs seen.
- **`config.py`** — every setting (room capacity, confidence threshold,
  camera index, model, log/screenshot toggles) lives in one file, no
  need to dig through `main.py` to tune the app.

## Requirements

- Python 3.9+ (3.12 recommended)
- A webcam
- Internet connection the *first* time you run it (to download YOLO weights)

## Setup

### 1. Create a virtual environment

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run it

```bash
python main.py
```

The first run will automatically download the `yolov8n.pt` model weights
(a small, fast YOLOv8 model pre-trained on the COCO dataset, which already
knows about people, chairs, backpacks, and 77 other everyday object types).

## Controls

| Key | Action |
|-----|--------|
| `Q` | Quit (prints a session summary to the console first) |
| `S` | Save a screenshot to `screenshots/` (shows an on-screen confirmation) |

## What you'll see

A live webcam window with:
- A colored bounding box + label/confidence on every detected person
  (green), chair (blue), backpack (orange), or book (purple)
- A dashboard panel in the top-left corner:
  ```
  VisionMag AI
  ─────────────────
  Persons        4
  Chairs        16
  Bags           2
  Books          0
  Occupancy    10%
  Empty Seats   12
  Confidence   89%
  FPS          14.2
  Time      11:40:02
  ```
- A "Screenshot Saved" banner for 2 seconds after pressing `S`

## Suggested Test Plan (for evaluation / NCSC report)

| Test | Scenario | What to check |
|------|----------|----------------|
| 1 | Just you in frame | `Person = 1` |
| 2 | You + a few friends | `Person` matches actual head count |
| 3 | Empty room with chairs | `Person = 0`, `Chair` matches actual chairs |
| 4 | Busy classroom | Compare AI counts to a manual count |

Record results in a table like:

| Test | Actual People | AI Count | Correct? |
|------|---------------:|---------:|:--------:|
| 1    | 1              | 1        | ✅ |
| 2    | 5              | 5        | ✅ |
| 3    | 18             | 17       | ❌ |

Save a screenshot (`S` key) for each test case as evidence — they land in
`screenshots/` automatically with a timestamped filename.

## Tuning (all in `config.py` now)

- **`CONFIDENCE_THRESHOLD`** (default `0.5`) — raise it to reduce false
  positives, lower it to catch more (but noisier) detections.
- **`ROOM_CAPACITY`** (default `40`) — used for the Occupancy % calculation.
- **`CAMERA_INDEX`** (default `0`) — change if you have multiple cameras.
- **`MODEL_NAME`** — swap `yolov8n.pt` for `yolov8s.pt` / `yolov8m.pt` for
  higher accuracy at the cost of speed (V1 testing showed undercounting
  in crowded/occluded scenes — a larger model is the first thing to try).
- **`SAVE_LOGS`** / **`SAVE_SCREENSHOTS`** — turn CSV logging or
  screenshots off entirely if you don't need them for a given test run.

## Reading the CSV log

`logs/session.csv` gets one row per second while the app runs:

```
timestamp,persons,chairs,bags,books,fps,occupancy
2026-08-02 11:35:01,12,31,8,0,14.2,30
```

Open it in Excel/Sheets to chart persons/occupancy over a class period —
this is the data for the "before / during / after class" experiment
below.

## Recommended Next Experiment

Test the same classroom at different times of day:

- Before class
- During class
- After class

For each, compare a manual head-count against the app's `Persons` count
and calculate an error percentage. This is the kind of before/during/after
comparison NCSC judges look for, and it will show you concretely where
detection breaks down (occlusion, distance from camera, low light, etc.)
so you know what to improve in V3.

## Roadmap

```
V1  Object Detection
V2  School Analytics        <- you are here
V3  Multiple Cameras
V4  Web Dashboard
V5  School Management AI
```

## Information

Created by Xtremerpie
