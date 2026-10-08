"""
Standards — the physical standard lines each log entry is measured against.

Carried over unchanged from the original MVP's logic (it was already
solid). Reps-based events: higher is better (lower_better=False).
Time-based events: stored in seconds, lower is better (lower_better=True).
Swap these for the real standards of the pipeline you're targeting.
"""

STANDARDS = {
    "pushups": {
        "label": "Push-ups (2 min)", "unit": "reps",
        "min": 50, "competitive": 80, "max": 100, "lower_better": False,
    },
    "situps": {
        "label": "Sit-ups (2 min)", "unit": "reps",
        "min": 60, "competitive": 85, "max": 100, "lower_better": False,
    },
    "pullups": {
        "label": "Pull-ups, dead hang", "unit": "reps",
        "min": 6, "competitive": 15, "max": 20, "lower_better": False,
    },
    "run_1_5mi": {
        "label": "1.5 mile run", "unit": "time",
        "min": 630, "competitive": 540, "max": 495, "lower_better": True,
    },
    "swim_500m": {
        "label": "500m swim", "unit": "time",
        "min": 750, "competitive": 570, "max": 480, "lower_better": True,
    },
}
EXERCISE_ORDER = ["pushups", "situps", "pullups", "run_1_5mi", "swim_500m"]


def format_seconds(total_seconds):
    """Convert seconds -> mm:ss for display."""
    total_seconds = int(round(total_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def parse_time_to_seconds(raw):
    """Parse 'mm:ss' or 'm:ss' input into seconds. Raises ValueError on bad input."""
    raw = raw.strip()
    if ":" not in raw:
        raise ValueError("Time must be in mm:ss format, e.g. 9:45")
    minutes_str, seconds_str = raw.split(":", 1)
    minutes = int(minutes_str)
    seconds = int(seconds_str)
    if seconds < 0 or seconds > 59 or minutes < 0:
        raise ValueError("Invalid mm:ss value")
    return minutes * 60 + seconds


def progress_ratio(value, std):
    """
    Return 0-1 progress between min and max standard, for a progress bar,
    and the tier the value currently falls in (below / min / competitive / max).
    """
    lo, comp, hi = std["min"], std["competitive"], std["max"]

    if std["lower_better"]:
        # Smaller is better: flip the scale so 0 = worst (min), 1 = best (max)
        # Note: value == lo lands in ratio 0.0 here but tier "min" below —
        # that's intentional (lo is the passing line, not a failing one).
        if value >= lo:
            ratio = 0.0
        elif value <= hi:
            ratio = 1.0
        else:
            ratio = (lo - value) / (lo - hi)
    else:
        if value <= lo:
            ratio = 0.0
        elif value >= hi:
            ratio = 1.0
        else:
            ratio = (value - lo) / (hi - lo)

    ratio = max(0.0, min(1.0, ratio))

    if std["lower_better"]:
        if value <= hi:
            tier = "max"
        elif value <= comp:
            tier = "competitive"
        elif value <= lo:
            tier = "min"
        else:
            tier = "below"
    else:
        if value >= hi:
            tier = "max"
        elif value >= comp:
            tier = "competitive"
        elif value >= lo:
            tier = "min"
        else:
            tier = "below"

    return ratio, tier


def display_value(value, std):
    return format_seconds(value) if std["unit"] == "time" else int(value)


def serialize_standards():
    """JSON-friendly view of STANDARDS + EXERCISE_ORDER for the mobile client."""
    return {
        "exercise_order": EXERCISE_ORDER,
        "standards": {
            key: {
                **std,
                "min_display": display_value(std["min"], std),
                "competitive_display": display_value(std["competitive"], std),
                "max_display": display_value(std["max"], std),
            }
            for key, std in STANDARDS.items()
        },
    }
