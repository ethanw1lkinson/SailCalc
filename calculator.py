"""Race handicap calculations.

This module converts elapsed times into corrected times using a simple yardstick
style calculation. The formula is intentionally straightforward so beginners can
follow it, while still being useful for mixed-fleet racing.
"""

from boats import get_boat_handicap


def parse_elapsed_time(value: str) -> int:
    """Parse a time string such as 35:00 or 1:02:03 into seconds."""
    text = str(value).strip()
    if not text:
        return 0

    parts = text.split(':')
    if len(parts) == 1:
        return int(float(parts[0])) * 60

    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds

    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds

    raise ValueError("Unsupported time format")


def format_time(total_seconds: int) -> str:
    """Convert seconds into HH:MM:SS when the value is large enough."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def calculate_corrected_time(elapsed_time: str, boat_class: str) -> int:
    """Calculate corrected time from elapsed seconds and boat handicap."""
    elapsed_seconds = parse_elapsed_time(elapsed_time)
    handicap = get_boat_handicap(boat_class)
    corrected_seconds = int(round(elapsed_seconds * (handicap / 100.0)))
    return corrected_seconds
