from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sailing_forecast.models import GeographySectorImpact, RaceArea, VenueGeographyProfile
from sailing_forecast.topography import SECTOR_NAMES, sector_name


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSM_CACHE_PATH = Path("data/osm_geography_cache.json")
SCAN_RADIUS_NM = 10.0
INNER_RING_NM = 5.0
WOOD_TAGS = {
    ("natural", "wood"),
    ("landuse", "forest"),
}
BUILT_UP_LANDUSE = {"residential", "commercial", "industrial", "retail", "construction"}


@dataclass(frozen=True)
class OsmFeature:
    feature_type: str
    latitude: float
    longitude: float
    distance_nm: float
    bearing_deg: float


class OpenStreetMapGeographyClient:
    def __init__(
        self,
        overpass_url: str = OVERPASS_URL,
        cache_path: Path = OSM_CACHE_PATH,
        timeout_seconds: int = 25,
    ) -> None:
        self.overpass_url = overpass_url
        self.cache_path = cache_path
        self.timeout_seconds = timeout_seconds
        self._cache = self._load_cache()

    def fetch_features(self, race_area: RaceArea) -> list[OsmFeature]:
        key = cache_key(race_area.latitude, race_area.longitude)
        cached = self._cache.get(key)
        if cached is None:
            payload = self._get_json(overpass_query(race_area.latitude, race_area.longitude, SCAN_RADIUS_NM * 1852))
            self._cache[key] = payload
            self._save_cache()
        else:
            payload = cached
        return parse_features(payload, race_area)

    def _get_json(self, query: str) -> dict:
        body = urlencode({"data": query}).encode("utf-8")
        request = Request(
            self.overpass_url,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "SailingForecastBuilder/0.1",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Overpass request failed ({exc.code}): {text}") from exc
        except URLError as exc:
            raise RuntimeError(f"Overpass request failed: {exc.reason}") from exc

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


def build_osm_geography_profile(
    race_area: RaceArea | None,
    client: OpenStreetMapGeographyClient | None = None,
) -> VenueGeographyProfile | None:
    if race_area is None:
        return None
    try:
        features = (client or OpenStreetMapGeographyClient()).fetch_features(race_area)
    except Exception:
        return None
    if not features:
        return VenueGeographyProfile(
            source="OpenStreetMap via Overpass API",
            radius_km=SCAN_RADIUS_NM * 1.852,
            summary=["OpenStreetMap scan found no wooded or built-up features within 10 nm of the race area."],
            feature_counts={"osm_wooded": 0, "osm_built_up": 0},
            sector_impacts=[],
        )

    wooded = [feature for feature in features if feature.feature_type == "wooded"]
    built_up = [feature for feature in features if feature.feature_type == "built_up"]
    summary = [
        (
            f"OpenStreetMap surface scan found {len(wooded)} wooded feature(s) and "
            f"{len(built_up)} built-up feature(s) within 10 nm of the race area."
        )
    ]
    summary.extend(ring_summary(wooded, built_up))
    summary.append("OSM source: OpenStreetMap contributors via Overpass API; feature tags are advisory and may be incomplete.")

    return VenueGeographyProfile(
        source="OpenStreetMap via Overpass API",
        radius_km=SCAN_RADIUS_NM * 1.852,
        summary=summary,
        feature_counts={"osm_wooded": len(wooded), "osm_built_up": len(built_up)},
        sector_impacts=osm_sector_impacts(features),
    )


def overpass_query(latitude: float, longitude: float, radius_m: float) -> str:
    area = f"around:{round(radius_m)},{latitude:.6f},{longitude:.6f}"
    return f"""
[out:json][timeout:25];
(
  way({area})["natural"="wood"];
  relation({area})["natural"="wood"];
  way({area})["landuse"="forest"];
  relation({area})["landuse"="forest"];
  way({area})["landuse"~"^(residential|commercial|industrial|retail|construction)$"];
  relation({area})["landuse"~"^(residential|commercial|industrial|retail|construction)$"];
);
out tags center qt;
"""


def parse_features(payload: dict, race_area: RaceArea) -> list[OsmFeature]:
    features: list[OsmFeature] = []
    for element in payload.get("elements", []):
        tags = element.get("tags") or {}
        feature_type = classify_tags(tags)
        if feature_type is None:
            continue
        center = element.get("center") or {}
        latitude = center.get("lat") or element.get("lat")
        longitude = center.get("lon") or element.get("lon")
        if latitude is None or longitude is None:
            continue
        distance_nm = distance_nautical_miles(race_area.latitude, race_area.longitude, float(latitude), float(longitude))
        if distance_nm > SCAN_RADIUS_NM:
            continue
        bearing = bearing_degrees(race_area.latitude, race_area.longitude, float(latitude), float(longitude))
        features.append(
            OsmFeature(
                feature_type=feature_type,
                latitude=float(latitude),
                longitude=float(longitude),
                distance_nm=distance_nm,
                bearing_deg=bearing,
            )
        )
    return features


def classify_tags(tags: dict[str, str]) -> str | None:
    if any(tags.get(key) == value for key, value in WOOD_TAGS) or "wood" in tags:
        return "wooded"
    if tags.get("landuse") in BUILT_UP_LANDUSE:
        return "built_up"
    return None


def ring_summary(wooded: list[OsmFeature], built_up: list[OsmFeature]) -> list[str]:
    inner_wooded = sum(1 for feature in wooded if feature.distance_nm <= INNER_RING_NM)
    outer_wooded = len(wooded) - inner_wooded
    inner_built = sum(1 for feature in built_up if feature.distance_nm <= INNER_RING_NM)
    outer_built = len(built_up) - inner_built
    return [
        f"Within 5 nm: {inner_wooded} wooded and {inner_built} built-up feature(s).",
        f"Between 5-10 nm: {outer_wooded} wooded and {outer_built} built-up feature(s).",
    ]


def osm_sector_impacts(features: list[OsmFeature]) -> list[GeographySectorImpact]:
    impacts: list[GeographySectorImpact] = []
    for sector in SECTOR_NAMES:
        sector_features = [feature for feature in features if sector_name(feature.bearing_deg) == sector]
        wooded = [feature for feature in sector_features if feature.feature_type == "wooded"]
        built_up = [feature for feature in sector_features if feature.feature_type == "built_up"]
        if not wooded and not built_up:
            continue
        notes = []
        if wooded:
            nearest = min(feature.distance_nm for feature in wooded)
            notes.append(f"{len(wooded)} wooded feature(s), nearest {nearest:.1f} nm")
        if built_up:
            nearest = min(feature.distance_nm for feature in built_up)
            notes.append(f"{len(built_up)} built-up feature(s), nearest {nearest:.1f} nm")
        impacts.append(
            GeographySectorImpact(
                sector=sector,
                feature="surface",
                count=len(sector_features),
                note=f"{sector} sector OSM surface roughness: {'; '.join(notes)}.",
            )
        )
    return impacts


def distance_nautical_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return (2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))) / 1.852


def bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return math.degrees(math.atan2(y, x)) % 360


def cache_key(latitude: float, longitude: float) -> str:
    return f"osm:{latitude:.4f},{longitude:.4f}:10nm:v2"
