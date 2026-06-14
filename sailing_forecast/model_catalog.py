from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherModel:
    provider: str
    model_id: str
    label: str
    region: str
    selectable: bool = True


AUTO_PRIMARY_MODEL = "auto_highest_resolution"

HIGHEST_RESOLUTION_MODEL_ORDER: tuple[str, ...] = (
    "meteofrance_arome_france_hd",
    "meteofrance_arome_france",
    "ukmo_uk_deterministic_2km",
    "meteofrance_arpege_europe",
    "ukmo_global_deterministic_10km",
    "meteofrance_arpege_world",
    "ecmwf_ifs025",
    "icon_global",
    "ecmwf_ifs04",
    "gfs_seamless",
)


OPEN_METEO_MODELS: tuple[WeatherModel, ...] = (
    WeatherModel("Open-Meteo", AUTO_PRIMARY_MODEL, "Highest resolution available", "Automatic"),
    WeatherModel("Open-Meteo", "gfs_seamless", "GFS seamless", "Global"),
    WeatherModel("Open-Meteo", "ecmwf_ifs025", "ECMWF IFS 0.25", "Global"),
    WeatherModel("Open-Meteo", "ecmwf_ifs04", "ECMWF IFS 0.4", "Global"),
    WeatherModel("Open-Meteo", "icon_global", "ICON global", "Global"),
    WeatherModel("Open-Meteo", "meteofrance_seamless", "Meteo-France seamless", "Automatic / Europe"),
    WeatherModel("Open-Meteo", "meteofrance_arpege_world", "Meteo-France ARPEGE world", "Global"),
    WeatherModel("Open-Meteo", "meteofrance_arpege_europe", "Meteo-France ARPEGE Europe", "Europe"),
    WeatherModel("Open-Meteo", "meteofrance_arome_france", "Meteo-France AROME France", "France region"),
    WeatherModel("Open-Meteo", "meteofrance_arome_france_hd", "Meteo-France AROME France HD", "France region"),
    WeatherModel("Open-Meteo", "ukmo_seamless", "UKMO seamless", "Automatic / UK-global"),
    WeatherModel("Open-Meteo", "ukmo_global_deterministic_10km", "UKMO global deterministic 10 km", "Global"),
    WeatherModel("Open-Meteo", "ukmo_uk_deterministic_2km", "UKMO UK deterministic 2 km", "UK region"),
)


WINDY_POINT_FORECAST_MODELS: tuple[WeatherModel, ...] = (
    WeatherModel("Windy", "arome", "Meteo-France AROME", "France and nearby areas", selectable=False),
    WeatherModel("Windy", "aromeFrance", "Meteo-France AROME France", "Metropolitan France", selectable=False),
    WeatherModel("Windy", "gfs", "GFS", "Global", selectable=False),
    WeatherModel("Windy", "icon", "ICON global", "Global", selectable=False),
    WeatherModel("Windy", "iconEu", "ICON Europe", "Europe", selectable=False),
)


def model_payload() -> dict[str, object]:
    return {
        "open_meteo": [model.__dict__ for model in OPEN_METEO_MODELS],
        "windy_point_forecast": [model.__dict__ for model in WINDY_POINT_FORECAST_MODELS],
        "default_primary": AUTO_PRIMARY_MODEL,
        "default_compare": [
            "gfs_seamless",
            "ecmwf_ifs025",
            "meteofrance_seamless",
            "ukmo_seamless",
        ],
    }
