"""Read/write the JSONL meal-rating log.

Keeps the original CLI write format (one JSON object per line with timestamp,
dish, rating) so data is interchangeable. Adds aggregation for the dashboard.
"""

import json
from collections import defaultdict
from datetime import datetime
from typing import Any

from app.config import settings


def append_rating(dish: str, rating: int) -> None:
    """Append a single rating entry. Caller is responsible for validation."""
    path = settings.rating_log
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dish": dish,
        "rating": int(rating),
    }
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def _read_entries() -> list[dict[str, Any]]:
    path = settings.rating_log
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # skip any corrupt line rather than failing the whole read
    return entries


def summarize() -> dict[str, Any]:
    """Aggregate ratings per dish: count, average, and last-rated timestamp."""
    entries = _read_entries()
    sums: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)
    last_rated: dict[str, str] = {}

    for entry in entries:
        dish = entry.get("dish")
        rating = entry.get("rating")
        timestamp = entry.get("timestamp", "")
        if not isinstance(dish, str) or not isinstance(rating, (int, float)):
            continue
        sums[dish] += int(rating)
        counts[dish] += 1
        if timestamp >= last_rated.get(dish, ""):
            last_rated[dish] = timestamp

    items = [
        {
            "dish": dish,
            "count": counts[dish],
            "average": round(sums[dish] / counts[dish], 2),
            "last_rated": last_rated.get(dish, ""),
        }
        for dish in counts
    ]
    # Highest rated first, then most-rated as a tiebreaker.
    items.sort(key=lambda item: (item["average"], item["count"]), reverse=True)

    return {"items": items, "total_ratings": sum(counts.values())}
