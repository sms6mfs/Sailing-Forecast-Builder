from __future__ import annotations

import json
import math
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import urlopen

from statistics import mean

from sailing_forecast.models import AreaForecastMap, AreaForecastPoint, ForecastHour, ForecastProfile, ForecastProfileLevel, ModelForecastRun, RaceArea, Venue
from sailing_forecast.weather_math import angular_difference, circular_mean, rounded_direction


WEATHER_HOURLY = (
    "temperature_2m",
    "pressure_msl",
    "cloud_cover",
    "cloud_cover_low",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "shortwave_radiation",
    "cape",
    "boundary_layer_height",
    "wind_speed_925hPa",
    "wind_direction_925hPa",
)

MARINE_HOURLY = (
    "wave_height",
    "wave_direction",
    "wave_period",
    "sea_surface_temperature",
    "ocean_current_velocity",
    "ocean_current_direction",
)


PROFILE_PRESSURE_LEVELS = (
    1000,
    975,
    950,
    925,
    900,
    850,
    800,
    700,
    600,
    500,
    400,
    300,
)
AREA_POINT_BATCH_SIZE = 180


class OpenMeteoClient:
    def fetch(self, venue: Venue, forecast_date: str, model: str | None = None, forecast_days: int = 1) -> list[ForecastHour]:
        end_date = forecast_end_date(forecast_date, forecast_days)
        params: dict[str, object] = {
            "latitude": venue.latitude,
            "longitude": venue.longitude,
            "timezone": venue.timezone,
            "start_date": forecast_date,
            "end_date": end_date,
            "wind_speed_unit": "kn",
            "hourly": ",".join(WEATHER_HOURLY),
        }
        if model:
            params["models"] = model
        weather = self._get_json(
            "https://api.open-meteo.com/v1/forecast",
            params,
        )
        try:
            marine = self._get_json(
                "https://marine-api.open-meteo.com/v1/marine",
                {
                    "latitude": venue.latitude,
                    "longitude": venue.longitude,
                    "timezone": venue.timezone,
                    "start_date": forecast_date,
                    "end_date": end_date,
                    "length_unit": "metric",
                    "cell_selection": "sea",
                    "hourly": ",".join(MARINE_HOURLY),
                },
            )
        except Exception:
            marine = None

        return _merge_hourly(weather["hourly"], None if marine is None else marine.get("hourly"))

    def fetch_profile(
        self,
        latitude: float,
        longitude: float,
        timezone: str,
        forecast_date: str,
        target_hour: int,
        model: str,
    ) -> ForecastProfile:
        hourly_variables = []
        for level in PROFILE_PRESSURE_LEVELS:
            hourly_variables.extend(
                (
                    f"temperature_{level}hPa",
                    f"relative_humidity_{level}hPa",
                    f"wind_speed_{level}hPa",
                    f"wind_direction_{level}hPa",
                    f"geopotential_height_{level}hPa",
                )
            )
        params: dict[str, object] = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "start_date": forecast_date,
            "end_date": forecast_date,
            "wind_speed_unit": "kn",
            "hourly": ",".join(hourly_variables),
            "models": model,
        }
        weather = self._get_json("https://api.open-meteo.com/v1/forecast", params)
        hourly = weather["hourly"]
        index = closest_hour_index(hourly["time"], target_hour)
        levels = [
            ForecastProfileLevel(
                pressure_hpa=level,
                temperature_c=_value(hourly, f"temperature_{level}hPa", index),
                relative_humidity_pct=_value(hourly, f"relative_humidity_{level}hPa", index),
                wind_speed_kt=_value(hourly, f"wind_speed_{level}hPa", index),
                wind_direction_deg=_value(hourly, f"wind_direction_{level}hPa", index),
                geopotential_height_m=_value(hourly, f"geopotential_height_{level}hPa", index),
            )
            for level in PROFILE_PRESSURE_LEVELS
        ]
        levels = [
            level
            for level in levels
            if level.temperature_c is not None
            or level.relative_humidity_pct is not None
            or level.wind_speed_kt is not None
            or level.wind_direction_deg is not None
        ]
        return ForecastProfile(
            model_name=model,
            time_label=datetime.fromisoformat(hourly["time"][index]).strftime("%H:%M local"),
            latitude=latitude,
            longitude=longitude,
            levels=levels,
        )

    def compare_models(
        self,
        venue: Venue,
        forecast_date: str,
        models: list[str],
        start_hour: int,
        end_hour: int,
    ) -> list[str]:
        runs, unavailable = self.fetch_model_runs(venue, forecast_date, models, start_hour, end_hour)
        return summarize_model_runs(runs, unavailable)

    def fetch_model_runs(
        self,
        venue: Venue,
        forecast_date: str,
        models: list[str],
        start_hour: int,
        end_hour: int,
        forecast_days: int = 1,
    ) -> tuple[list[ModelForecastRun], list[str]]:
        summaries: list[str] = []
        model_runs: list[ModelForecastRun] = []
        for model in models:
            try:
                hours = [
                    hour
                    for hour in self.fetch(venue, forecast_date, model=model, forecast_days=forecast_days)
                    if start_hour <= hour.time.hour <= end_hour
                ]
                if hours:
                    model_runs.append(ModelForecastRun(name=model, hours=hours))
            except Exception as exc:
                summaries.append(f"{model}: unavailable ({exc})")
        return model_runs, summaries

    def fetch_area_points(
        self,
        race_area: RaceArea,
        forecast_date: str,
        target_hour: int,
        model: str | None = None,
        grid_size: int = 9,
    ) -> list[AreaForecastPoint]:
        points = grid_points(race_area, grid_size=grid_size)
        results: list[AreaForecastPoint] = []
        for point_batch in chunked(points, AREA_POINT_BATCH_SIZE):
            results.extend(
                self._fetch_area_points_batch(
                    points=point_batch,
                    forecast_date=forecast_date,
                    target_hour=target_hour,
                    model=model,
                )
            )
        return results

    def _fetch_area_points_batch(
        self,
        points: list[tuple[float, float]],
        forecast_date: str,
        target_hour: int,
        model: str | None = None,
    ) -> list[AreaForecastPoint]:
        results: list[AreaForecastPoint] = []
        params: dict[str, object] = {
            "latitude": ",".join(f"{latitude:.5f}" for latitude, _ in points),
            "longitude": ",".join(f"{longitude:.5f}" for _, longitude in points),
            "timezone": "auto",
            "start_date": forecast_date,
            "end_date": forecast_date,
            "wind_speed_unit": "kn",
            "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,pressure_msl",
        }
        if model:
            params["models"] = model
        weather = self._get_json("https://api.open-meteo.com/v1/forecast", params)
        locations = weather if isinstance(weather, list) else [weather]
        for (latitude, longitude), location in zip(points, locations):
            try:
                hourly = location["hourly"]
                index = closest_hour_index(hourly["time"], target_hour)
                results.append(
                    AreaForecastPoint(
                        latitude=latitude,
                        longitude=longitude,
                        wind_direction_10m=_value(hourly, "wind_direction_10m", index) or 0.0,
                        wind_speed_10m=_value(hourly, "wind_speed_10m", index) or 0.0,
                        wind_gust_10m=_value(hourly, "wind_gusts_10m", index) or 0.0,
                        cloud_cover=_value(hourly, "cloud_cover", index),
                        sea_level_pressure=_value(hourly, "pressure_msl", index),
                    )
                )
            except Exception:
                continue
        return results

    def fetch_area_maps(
        self,
        race_area: RaceArea,
        forecast_date: str,
        target_hours: list[int],
        model: str | None = None,
        grid_size: int = 9,
    ) -> list[AreaForecastMap]:
        points = grid_points(race_area, grid_size=grid_size)
        maps_by_hour: dict[int, list[AreaForecastPoint]] = {target_hour: [] for target_hour in target_hours}
        for point_batch in chunked(points, AREA_POINT_BATCH_SIZE):
            batch_maps = self._fetch_area_maps_batch(
                points=point_batch,
                forecast_date=forecast_date,
                target_hours=target_hours,
                model=model,
            )
            for area_map in batch_maps:
                maps_by_hour.setdefault(area_map.hour, []).extend(area_map.points)
        return [
            AreaForecastMap(hour=target_hour, time_label=f"{target_hour:02d}:00 local", points=maps_by_hour.get(target_hour, []))
            for target_hour in target_hours
        ]

    def _fetch_area_maps_batch(
        self,
        points: list[tuple[float, float]],
        forecast_date: str,
        target_hours: list[int],
        model: str | None = None,
    ) -> list[AreaForecastMap]:
        params: dict[str, object] = {
            "latitude": ",".join(f"{latitude:.5f}" for latitude, _ in points),
            "longitude": ",".join(f"{longitude:.5f}" for _, longitude in points),
            "timezone": "auto",
            "start_date": forecast_date,
            "end_date": forecast_date,
            "wind_speed_unit": "kn",
            "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,pressure_msl",
        }
        if model:
            params["models"] = model
        weather = self._get_json("https://api.open-meteo.com/v1/forecast", params)
        locations = weather if isinstance(weather, list) else [weather]
        maps: list[AreaForecastMap] = []
        for target_hour in target_hours:
            map_points: list[AreaForecastPoint] = []
            for (latitude, longitude), location in zip(points, locations):
                try:
                    hourly = location["hourly"]
                    index = closest_hour_index(hourly["time"], target_hour)
                    map_points.append(
                        AreaForecastPoint(
                            latitude=latitude,
                            longitude=longitude,
                            wind_direction_10m=_value(hourly, "wind_direction_10m", index) or 0.0,
                            wind_speed_10m=_value(hourly, "wind_speed_10m", index) or 0.0,
                            wind_gust_10m=_value(hourly, "wind_gusts_10m", index) or 0.0,
                            cloud_cover=_value(hourly, "cloud_cover", index),
                            sea_level_pressure=_value(hourly, "pressure_msl", index),
                        )
                    )
                except Exception:
                    continue
            maps.append(AreaForecastMap(hour=target_hour, time_label=f"{target_hour:02d}:00 local", points=map_points))
        return maps

    def _get_json(self, base_url: str, params: dict[str, object]) -> dict:
        url = f"{base_url}?{urlencode(params, safe=',')}"
        try:
            with urlopen(url, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Open-Meteo request failed ({exc.code}): {body}") from exc


def summarize_model_runs(model_runs: list[ModelForecastRun], unavailable: list[str] | None = None) -> list[str]:
    summaries = list(unavailable or [])
    if not model_runs:
        return summaries

    for run in model_runs:
        avg_dir = circular_mean([hour.wind_direction_10m for hour in run.hours])
        avg_speed = mean(hour.wind_speed_10m for hour in run.hours)
        summaries.append(f"{run.name}: averages {rounded_direction(avg_dir):03d} at {round(avg_speed)} kt.")

    if len(model_runs) >= 2:
        avg_dirs = [circular_mean([hour.wind_direction_10m for hour in run.hours]) for run in model_runs]
        avg_speeds = [mean(hour.wind_speed_10m for hour in run.hours) for run in model_runs]
        dir_spread = max(angular_difference(avg_dirs[0], direction) for direction in avg_dirs[1:])
        speed_spread = max(avg_speeds) - min(avg_speeds)
        summaries.append(
            f"Model spread: direction spread about {round(dir_spread)} degrees; speed spread about {speed_spread:.1f} kt."
        )
    return summaries


def _merge_hourly(weather: dict, marine: dict | None) -> list[ForecastHour]:
    marine_by_time = {}
    if marine:
        marine_by_time = {
            time: index for index, time in enumerate(marine.get("time", []))
        }

    hours: list[ForecastHour] = []
    for index, time_text in enumerate(weather["time"]):
        marine_index = marine_by_time.get(time_text)
        hours.append(
            ForecastHour(
                time=datetime.fromisoformat(time_text),
                temperature_2m=_value(weather, "temperature_2m", index),
                sea_level_pressure=_value(weather, "pressure_msl", index),
                cloud_cover=_value(weather, "cloud_cover", index),
                cloud_cover_low=_value(weather, "cloud_cover_low", index),
                wind_speed_10m=_value(weather, "wind_speed_10m", index) or 0.0,
                wind_direction_10m=_value(weather, "wind_direction_10m", index) or 0.0,
                wind_gust_10m=_value(weather, "wind_gusts_10m", index) or 0.0,
                shortwave_radiation=_value(weather, "shortwave_radiation", index),
                cape=_value(weather, "cape", index),
                boundary_layer_height=_value(weather, "boundary_layer_height", index),
                wind_speed_925hpa=_value(weather, "wind_speed_925hPa", index),
                wind_direction_925hpa=_value(weather, "wind_direction_925hPa", index),
                sea_surface_temperature=_marine_value(marine, marine_index, "sea_surface_temperature"),
                wave_height=_marine_value(marine, marine_index, "wave_height"),
                wave_direction=_marine_value(marine, marine_index, "wave_direction"),
                wave_period=_marine_value(marine, marine_index, "wave_period"),
                ocean_current_velocity=_marine_value(marine, marine_index, "ocean_current_velocity"),
                ocean_current_direction=_marine_value(marine, marine_index, "ocean_current_direction"),
            )
        )
    return hours


def _value(hourly: dict, key: str, index: int) -> float | None:
    values = hourly.get(key)
    if not values:
        return None
    return values[index]


def _marine_value(marine: dict | None, index: int | None, key: str) -> float | None:
    if marine is None or index is None:
        return None
    values = marine.get(key)
    if not values:
        return None
    return values[index]


def grid_points(race_area: RaceArea, grid_size: int = 9) -> list[tuple[float, float]]:
    half = max(1, grid_size // 2)
    lat_step = (race_area.radius_nm * 1.852) / 111.0 / 2
    lon_step = lat_step / max(0.2, abs(math.cos(math.radians(race_area.latitude))))
    points: list[tuple[float, float]] = []
    for y in range(-half, half + 1):
        for x in range(-half, half + 1):
            points.append((race_area.latitude + y * lat_step, race_area.longitude + x * lon_step))
    return points


def chunked(items: list[tuple[float, float]], size: int) -> list[list[tuple[float, float]]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def closest_hour_index(times: list[str], target_hour: int) -> int:
    best_index = 0
    best_delta = 24
    for index, time_text in enumerate(times):
        hour = datetime.fromisoformat(time_text).hour
        delta = abs(hour - target_hour)
        if delta < best_delta:
            best_index = index
            best_delta = delta
    return best_index


def forecast_end_date(forecast_date: str, forecast_days: int) -> str:
    days = max(1, min(2, int(forecast_days or 1)))
    start = datetime.fromisoformat(forecast_date).date()
    return (start + timedelta(days=days - 1)).isoformat()
