from __future__ import annotations

import math


def circular_mean(degrees: list[float]) -> float:
    if not degrees:
        raise ValueError("degrees must not be empty")
    sin_sum = sum(math.sin(math.radians(value)) for value in degrees)
    cos_sum = sum(math.cos(math.radians(value)) for value in degrees)
    return math.degrees(math.atan2(sin_sum, cos_sum)) % 360


def angular_difference(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def rounded_direction(degrees: float, step: int = 10) -> int:
    return int(round(degrees / step) * step) % 360


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
