from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from sailing_forecast.models import GeographySectorImpact, RaceArea, Venue, VenueGeographyProfile


OPEN_TOPO_DATA_URL = "https://api.opentopodata.org/v1/eudem25m"
ELEVATION_CACHE_PATH = Path("data/elevation_cache.json")
SECTOR_NAMES = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
ELEVATION_BATCH_SIZE = 90
TERRAIN_BOX_RADIUS_NM = 10.0
TERRAIN_BOX_GRID_SIZE = 21


@dataclass(frozen=True)
class TerrainSample:
    latitude: float
    longitude: float
    bearing_deg: float
    distance_km: float
    elevation_m: float | None
    dataset: str | None = None


class OpenTopoDataClient:
    def __init__(
        self,
        base_url: str = OPEN_TOPO_DATA_URL,
        cache_path: Path = ELEVATION_CACHE_PATH,
        timeout_seconds: int = 12,
    ) -> None:
        self.base_url = base_url
        self.cache_path = cache_path
        self.timeout_seconds = timeout_seconds
        self._cache = self._load_cache()

    def fetch_elevations(self, locations: list[tuple[float, float]]) -> list[tuple[float | None, str | None]]:
        if not locations:
            return []

        results: list[tuple[float | None, str | None] | None] = []
        missing: list[tuple[int, float, float, str]] = []
        for index, (latitude, longitude) in enumerate(locations):
            key = cache_key(latitude, longitude)
            cached = self._cache.get(key)
            if cached is None:
                results.append(None)
                missing.append((index, latitude, longitude, key))
            else:
                results.append((cached.get("elevation"), cached.get("dataset")))

        for batch in chunked_missing(missing, ELEVATION_BATCH_SIZE):
            locations_text = "|".join(f"{latitude:.5f},{longitude:.5f}" for _, latitude, longitude, _ in batch)
            params = {"locations": locations_text, "interpolation": "bilinear", "nodata_value": "null"}
            payload = self._get_json(params)
            if payload.get("status") != "OK":
                raise RuntimeError(payload.get("error") or "Open Topo Data request failed")
            for (index, _, _, key), item in zip(batch, payload.get("results", [])):
                elevation = item.get("elevation")
                dataset = item.get("dataset")
                cache_item = {
                    "elevation": None if elevation is None else float(elevation),
                    "dataset": dataset,
                }
                self._cache[key] = cache_item
                results[index] = (cache_item["elevation"], cache_item["dataset"])
        if missing:
            self._save_cache()

        return [item if item is not None else (None, None) for item in results]

    def _get_json(self, params: dict[str, str]) -> dict:
        url = f"{self.base_url}?{urlencode(params, safe=',|')}"
        try:
            with urlopen(url, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Open Topo Data request failed ({exc.code}): {body}") from exc
        except URLError as exc:
            raise RuntimeError(f"Open Topo Data request failed: {exc.reason}") from exc

    def _load_cache(self) -> dict[str, dict[str, object]]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open("w", encoding="utf-8") as file:
            json.dump(self._cache, file, indent=2, sort_keys=True)


def build_terrain_profile(
    venue: Venue,
    race_area: RaceArea | None,
    client: OpenTopoDataClient | None = None,
) -> VenueGeographyProfile | None:
    target = race_area or RaceArea("Venue", venue.latitude, venue.longitude, 1.5)
    if not is_eudem_candidate(target.latitude, target.longitude):
        return None
    samples = terrain_sample_points(target)
    try:
        elevations = (client or OpenTopoDataClient()).fetch_elevations(
            [(sample.latitude, sample.longitude) for sample in samples]
        )
    except Exception:
        return None

    enriched = [
        TerrainSample(
            latitude=sample.latitude,
            longitude=sample.longitude,
            bearing_deg=sample.bearing_deg,
            distance_km=sample.distance_km,
            elevation_m=elevation,
            dataset=dataset,
        )
        for sample, (elevation, dataset) in zip(samples, elevations)
    ]
    valid = [sample for sample in enriched if sample.elevation_m is not None]
    if not valid:
        return VenueGeographyProfile(
            source="Open Topo Data eudem25m / EU-DEM v1.1",
            radius_km=terrain_scan_radius_km(target),
            summary=[
                "EU-DEM returned no land elevations in the terrain scan; offshore or outside-coverage points are ignored."
            ],
            feature_counts={"samples": len(enriched), "valid_eudem": 0},
            sector_impacts=[],
        )

    elevations_m = [sample.elevation_m or 0 for sample in valid]
    max_sample = max(valid, key=lambda sample: sample.elevation_m or -9999)
    min_elevation = min(elevations_m)
    max_elevation = max(elevations_m)
    avg_elevation = mean(elevations_m)
    relief = max_elevation - min_elevation
    sector_impacts = terrain_sector_impacts(valid)
    summary = [
        (
            f"EU-DEM terrain scan found {round(min_elevation)}-{round(max_elevation)} m land elevations "
            f"inside a {TERRAIN_BOX_RADIUS_NM:g} nm half-width box around {target.name}; mean sampled land height is {round(avg_elevation)} m."
        ),
        (
            f"Highest sampled terrain is {round(max_sample.elevation_m or 0)} m "
            f"{sector_name(max_sample.bearing_deg)} of the race area, about {max_sample.distance_km / 1.852:.0f} nm away."
        ),
    ]
    if relief >= 80:
        summary.append("Local relief is large enough to flag terrain bends, gust lines or lee effects when flow crosses land before the course.")
    elif relief >= 30:
        summary.append("Local relief is moderate; use wind-sector checks for small bends or pressure differences near the shoreline.")
    else:
        summary.append("Sampled land relief is low, so DEM terrain is unlikely to dominate the local wind pattern.")
    summary.append("Terrain source: Open Topo Data eudem25m, EU-DEM v1.1. Derived notes are advisory and do not imply Copernicus endorsement.")

    return VenueGeographyProfile(
        source="Open Topo Data eudem25m / EU-DEM v1.1",
        radius_km=terrain_scan_radius_km(target),
        summary=summary,
        feature_counts={"samples": len(enriched), "valid_eudem": len(valid)},
        sector_impacts=sector_impacts,
    )


def terrain_sample_points(race_area: RaceArea) -> list[TerrainSample]:
    half = TERRAIN_BOX_GRID_SIZE // 2
    radius_km = TERRAIN_BOX_RADIUS_NM * 1.852
    lat_step = radius_km / 111.0 / max(1, half)
    lon_step = lat_step / max(0.2, abs(math.cos(math.radians(race_area.latitude))))
    samples: list[TerrainSample] = []
    for y in range(-half, half + 1):
        for x in range(-half, half + 1):
            north_km = y * radius_km / max(1, half)
            east_km = x * radius_km / max(1, half)
            distance_km = math.hypot(north_km, east_km)
            bearing = 0.0 if distance_km == 0 else (math.degrees(math.atan2(east_km, north_km)) + 360) % 360
            samples.append(
                TerrainSample(
                    latitude=race_area.latitude + y * lat_step,
                    longitude=race_area.longitude + x * lon_step,
                    bearing_deg=bearing,
                    distance_km=distance_km,
                    elevation_m=None,
                )
            )
    return samples


def terrain_scan_radius_km(race_area: RaceArea) -> float:
    return TERRAIN_BOX_RADIUS_NM * 1.852


def destination_point(latitude: float, longitude: float, bearing_deg: float, distance_km: float) -> tuple[float, float]:
    radius_km = 6371.0088
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(latitude)
    lon1 = math.radians(longitude)
    angular_distance = distance_km / radius_km
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), ((math.degrees(lon2) + 540) % 360) - 180


def terrain_sector_impacts(samples: list[TerrainSample]) -> list[GeographySectorImpact]:
    by_sector: dict[str, list[TerrainSample]] = {}
    for sample in samples:
        if sample.distance_km == 0 or sample.elevation_m is None:
            continue
        by_sector.setdefault(sector_name(sample.bearing_deg), []).append(sample)

    impacts: list[GeographySectorImpact] = []
    for sector, sector_samples in by_sector.items():
        high = max(sector_samples, key=lambda sample: sample.elevation_m or -9999)
        average = mean(sample.elevation_m or 0 for sample in sector_samples)
        if (high.elevation_m or 0) < 35 and average < 20:
            continue
        impacts.append(
            GeographySectorImpact(
                sector=sector,
                feature="terrain",
                count=len(sector_samples),
                note=f"{sector} sector sampled land averages {round(average)} m and peaks near {round(high.elevation_m or 0)} m.",
            )
        )
    return sorted(impacts, key=lambda impact: SECTOR_NAMES.index(impact.sector))


def sector_name(bearing_deg: float) -> str:
    return SECTOR_NAMES[int(((bearing_deg % 360) + 22.5) // 45) % len(SECTOR_NAMES)]


def cache_key(latitude: float, longitude: float) -> str:
    return f"eudem25m:{latitude:.5f},{longitude:.5f}"


def is_eudem_candidate(latitude: float, longitude: float) -> bool:
    return 24.0 <= latitude <= 72.5 and -32.0 <= longitude <= 45.0


def chunked_missing(
    items: list[tuple[int, float, float, str]],
    size: int,
) -> list[list[tuple[int, float, float, str]]]:
    return [items[index:index + size] for index in range(0, len(items), size)]
