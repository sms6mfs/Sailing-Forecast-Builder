from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RaceArea:
    name: str
    latitude: float
    longitude: float
    radius_nm: float
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SectorRule:
    name: str
    start_deg: int
    end_deg: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class Venue:
    key: str
    name: str
    latitude: float
    longitude: float
    timezone: str
    shoreline_axis_deg: int
    notes: tuple[str, ...]
    race_areas: tuple[RaceArea, ...] = ()
    sector_rules: tuple[SectorRule, ...] = ()
    default_models: tuple[str, ...] = ("auto_highest_resolution", "gfs_seamless", "ecmwf_ifs025", "meteofrance_seamless", "ukmo_seamless")


@dataclass(frozen=True)
class EventMetadata:
    name: str = "Training forecast"
    team: str | None = None
    forecaster: str = "Sailing Forecast Builder"
    issue_time: str | None = None
    synoptic_chart_url: str | None = "https://www.weathercharts.org/ukmomslp.htm#t0"


@dataclass(frozen=True)
class ForecastHour:
    time: datetime
    wind_direction_10m: float
    wind_speed_10m: float
    wind_gust_10m: float
    wind_direction_925hpa: float | None
    wind_speed_925hpa: float | None
    sea_level_pressure: float | None
    cloud_cover: float | None
    cloud_cover_low: float | None
    boundary_layer_height: float | None
    cape: float | None
    shortwave_radiation: float | None
    temperature_2m: float | None
    sea_surface_temperature: float | None = None
    wave_height: float | None = None
    wave_direction: float | None = None
    wave_period: float | None = None
    ocean_current_velocity: float | None = None
    ocean_current_direction: float | None = None


@dataclass(frozen=True)
class AreaForecastPoint:
    latitude: float
    longitude: float
    wind_direction_10m: float
    wind_speed_10m: float
    wind_gust_10m: float
    cloud_cover: float | None
    sea_level_pressure: float | None


@dataclass(frozen=True)
class AreaForecastMap:
    hour: int
    time_label: str
    points: list[AreaForecastPoint]


@dataclass(frozen=True)
class ModelForecastRun:
    name: str
    hours: list[ForecastHour]


@dataclass(frozen=True)
class ForecastProfileLevel:
    pressure_hpa: int
    temperature_c: float | None
    relative_humidity_pct: float | None
    wind_speed_kt: float | None
    wind_direction_deg: float | None
    geopotential_height_m: float | None


@dataclass(frozen=True)
class ForecastProfile:
    model_name: str
    time_label: str
    latitude: float
    longitude: float
    levels: list[ForecastProfileLevel]


@dataclass(frozen=True)
class GeographySectorImpact:
    sector: str
    feature: str
    count: int
    note: str


@dataclass(frozen=True)
class VenueGeographyProfile:
    source: str
    radius_km: float
    summary: list[str]
    feature_counts: dict[str, int]
    sector_impacts: list[GeographySectorImpact]


@dataclass(frozen=True)
class SailingHour:
    time_label: str
    twd_mean: int
    twd_min: int
    twd_max: int
    tws_mean: int
    tws_min: int
    tws_max: int
    gust: int
    lull: int
    phase: str
    note: str


@dataclass(frozen=True)
class SailingForecast:
    venue: Venue
    event: EventMetadata
    race_area: RaceArea | None
    forecast_date: str
    race_window: str
    model_name: str
    type_of_day: str
    confidence: str
    executive_summary: str
    meteorology: list[str]
    local_effects: list[str]
    geography_profile: VenueGeographyProfile | None
    hours: list[SailingHour]
    source_hours: list[ForecastHour]
    area_points: list[AreaForecastPoint]
    area_map_time: str | None
    area_maps: list[AreaForecastMap]
    area_map_mode: str
    model_summaries: list[str]
    marine_summary: str | None
    model_runs: list[ModelForecastRun] = field(default_factory=list)
    profile: ForecastProfile | None = None
