from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sailing_forecast.weather_math import angular_difference


OBSERVATION_FIELDS = (
    "timestamp",
    "venue_key",
    "race_area",
    "time_local",
    "twd",
    "tws",
    "gust",
    "notes",
)


@dataclass(frozen=True)
class Observation:
    venue_key: str
    race_area: str
    time_local: str
    twd: int
    tws: float
    gust: float
    notes: str = ""


def append_observation(path: Path, observation: Observation) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=OBSERVATION_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "venue_key": observation.venue_key,
                "race_area": observation.race_area,
                "time_local": observation.time_local,
                "twd": observation.twd,
                "tws": observation.tws,
                "gust": observation.gust,
                "notes": observation.notes,
            }
        )


def load_observations(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def summarize_bias(path: Path, venue_key: str | None = None) -> dict[str, object]:
    rows = load_observations(path)
    if venue_key:
        rows = [row for row in rows if row.get("venue_key") == venue_key]
    return {
        "observation_count": len(rows),
        "venues": sorted({row.get("venue_key", "") for row in rows if row.get("venue_key")}),
        "message": "Observation capture is active. Forecast-vs-observed bias will be calculated once forecast snapshots are stored with each observation.",
    }


def simple_bias_from_pairs(pairs: list[tuple[float, float, float, float]]) -> dict[str, float]:
    if not pairs:
        return {"direction_bias_deg": 0.0, "speed_bias_kt": 0.0}
    direction_errors = [angular_difference(forecast_dir, observed_dir) for forecast_dir, observed_dir, _, _ in pairs]
    speed_errors = [observed_speed - forecast_speed for _, _, forecast_speed, observed_speed in pairs]
    return {
        "direction_bias_deg": sum(direction_errors) / len(direction_errors),
        "speed_bias_kt": sum(speed_errors) / len(speed_errors),
    }
