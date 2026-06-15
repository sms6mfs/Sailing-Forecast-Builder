from __future__ import annotations

from dataclasses import replace

from sailing_forecast.analysis import analyze_forecast
from sailing_forecast.model_catalog import AUTO_PRIMARY_MODEL, HIGHEST_RESOLUTION_MODEL_ORDER
from sailing_forecast.models import AreaForecastMap, AreaForecastPoint, EventMetadata, ForecastHour, ForecastProfile, GeographySectorImpact, ModelForecastRun, RaceArea, SailingForecast, Venue, VenueGeographyProfile
from sailing_forecast.open_meteo import OpenMeteoClient, summarize_model_runs
from sailing_forecast.osm_geography import build_osm_geography_profile
from sailing_forecast.render_html import render_forecast_html
from sailing_forecast.render_text import render_forecast_text
from sailing_forecast.topography import build_terrain_profile
from sailing_forecast.venues import VENUES


AREA_MAP_HOURS = [11, 13, 15, 17]
PRESSURE_LEVEL_WIND_MODEL = "ecmwf_ifs025"
BOUNDARY_LAYER_MODEL = "gfs_seamless"
PROFILE_MODEL = "ecmwf_ifs025"
DEFAULT_AREA_GRID_SIZE = 15
DEFAULT_FORECAST_DAYS = 1


def build_forecast(
    venue_key: str,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    event: EventMetadata | None = None,
    race_area_name: str | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> SailingForecast:
    if venue_key not in VENUES:
        raise ValueError("Unknown saved venue. Use a custom venue with latitude and longitude.")
    venue = VENUES[venue_key]
    return build_forecast_for_venue(
        venue=venue,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )


def build_forecast_for_venue(
    venue: Venue,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    event: EventMetadata | None = None,
    race_area_name: str | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> SailingForecast:
    race_area = find_race_area(venue.race_areas, race_area_name)
    client = OpenMeteoClient()
    requested_model = normalize_primary_model(model)
    normalized_forecast_days = normalize_forecast_days(forecast_days)
    resolved_model, hours = fetch_primary_forecast(client, venue, forecast_date, requested_model, normalized_forecast_days)
    hours, pressure_level_note = fill_missing_925hpa_winds(
        client=client,
        venue=venue,
        forecast_date=forecast_date,
        hours=hours,
        primary_model=resolved_model,
        forecast_days=normalized_forecast_days,
    )
    hours, boundary_layer_note = fill_missing_boundary_layer(
        client=client,
        venue=venue,
        forecast_date=forecast_date,
        hours=hours,
        primary_model=resolved_model,
        forecast_days=normalized_forecast_days,
    )
    area_points = []
    area_map_time = None
    area_maps = []
    area_map_note = None
    normalized_grid_size = normalize_area_grid_size(area_grid_size)
    if race_area:
        try:
            area_maps = client.fetch_area_maps(
                race_area=race_area,
                forecast_date=forecast_date,
                target_hours=AREA_MAP_HOURS,
                model=resolved_model,
                grid_size=normalized_grid_size,
            )
            target_hour = 13
            area_map_time = f"{target_hour:02d}00 local"
            area_points = next((area_map.points for area_map in area_maps if area_map.hour == target_hour), [])
        except Exception as exc:
            area_map_note = f"Forecast area grid unavailable ({exc})."
    model_summaries = []
    model_runs = [ModelForecastRun(name=resolved_model, hours=[hour for hour in hours if start_hour <= hour.time.hour <= end_hour])]
    if compare_models:
        comparison_models = [
            item
            for item in compare_models
            if item not in {requested_model, resolved_model, AUTO_PRIMARY_MODEL}
        ]
        comparison_runs, unavailable_models = client.fetch_model_runs(
            venue=venue,
            forecast_date=forecast_date,
            models=comparison_models,
            start_hour=start_hour,
            end_hour=end_hour,
            forecast_days=normalized_forecast_days,
        )
        model_runs.extend(comparison_runs)
        model_summaries = summarize_model_runs(comparison_runs, unavailable_models)
    if pressure_level_note:
        model_summaries.append(pressure_level_note)
    if boundary_layer_note:
        model_summaries.append(boundary_layer_note)
    if area_map_note:
        model_summaries.append(area_map_note)
    profile, profile_note = fetch_profile(
        client=client,
        venue=venue,
        race_area=race_area,
        forecast_date=forecast_date,
        target_hour=round((start_hour + end_hour) / 2),
    )
    if profile_note:
        model_summaries.append(profile_note)
    geography_profile = build_geography_profile(venue, race_area)
    return analyze_forecast(
        venue=venue,
        event=event or EventMetadata(),
        race_area=race_area,
        forecast_date=forecast_date,
        forecast_hours=hours,
        start_hour=start_hour,
        end_hour=end_hour,
        model_name=resolved_model,
        model_summaries=model_summaries,
        model_runs=model_runs,
        area_points=area_points,
        area_map_time=area_map_time,
        area_maps=area_maps,
        area_map_mode=normalize_area_map_mode(area_map_mode),
        geography_profile=geography_profile,
        profile=profile,
    )


def normalize_primary_model(model: str | None) -> str:
    if not model:
        return AUTO_PRIMARY_MODEL
    return model


def fetch_primary_forecast(
    client: OpenMeteoClient,
    venue: Venue,
    forecast_date: str,
    requested_model: str,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> tuple[str, list[ForecastHour]]:
    if requested_model != AUTO_PRIMARY_MODEL:
        return requested_model, client.fetch(venue, forecast_date, model=requested_model, forecast_days=forecast_days)

    failures: list[str] = []
    for candidate in HIGHEST_RESOLUTION_MODEL_ORDER:
        try:
            hours = client.fetch(venue, forecast_date, model=candidate, forecast_days=forecast_days)
        except Exception as exc:
            failures.append(f"{candidate}: {exc}")
            continue
        if hours:
            return candidate, hours
        failures.append(f"{candidate}: no hourly data")
    detail = "; ".join(failures[:4])
    raise RuntimeError(f"No explicit Open-Meteo model was available for this venue/date. {detail}")


def fill_missing_925hpa_winds(
    client: OpenMeteoClient,
    venue: Venue,
    forecast_date: str,
    hours: list[ForecastHour],
    primary_model: str,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> tuple[list[ForecastHour], str | None]:
    missing = [
        hour
        for hour in hours
        if hour.wind_speed_925hpa is None or hour.wind_direction_925hpa is None
    ]
    if not missing or primary_model == PRESSURE_LEVEL_WIND_MODEL:
        return hours, None

    try:
        fallback_hours = client.fetch(venue, forecast_date, model=PRESSURE_LEVEL_WIND_MODEL, forecast_days=forecast_days)
    except Exception as exc:
        return hours, f"925 hPa wind unavailable from {primary_model}; ECMWF fallback failed ({exc})."

    fallback_by_time = {hour.time: hour for hour in fallback_hours}
    filled = 0
    merged: list[ForecastHour] = []
    for hour in hours:
        fallback = fallback_by_time.get(hour.time)
        if (
            fallback is not None
            and (hour.wind_speed_925hpa is None or hour.wind_direction_925hpa is None)
            and fallback.wind_speed_925hpa is not None
            and fallback.wind_direction_925hpa is not None
        ):
            merged.append(
                replace(
                    hour,
                    wind_speed_925hpa=fallback.wind_speed_925hpa,
                    wind_direction_925hpa=fallback.wind_direction_925hpa,
                )
            )
            filled += 1
        else:
            merged.append(hour)

    if filled:
        return merged, f"925 hPa wind filled from {PRESSURE_LEVEL_WIND_MODEL}; primary surface model is {primary_model}."
    return hours, f"925 hPa wind unavailable from {primary_model}; {PRESSURE_LEVEL_WIND_MODEL} returned no matching pressure-level wind."


def fill_missing_boundary_layer(
    client: OpenMeteoClient,
    venue: Venue,
    forecast_date: str,
    hours: list[ForecastHour],
    primary_model: str,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> tuple[list[ForecastHour], str | None]:
    missing = [hour for hour in hours if hour.boundary_layer_height is None]
    if not missing or primary_model == BOUNDARY_LAYER_MODEL:
        return hours, None

    try:
        fallback_hours = client.fetch(venue, forecast_date, model=BOUNDARY_LAYER_MODEL, forecast_days=forecast_days)
    except Exception as exc:
        return hours, f"Boundary layer height unavailable from {primary_model}; GFS fallback failed ({exc})."

    fallback_by_time = {hour.time: hour for hour in fallback_hours}
    filled = 0
    merged: list[ForecastHour] = []
    for hour in hours:
        fallback = fallback_by_time.get(hour.time)
        if (
            fallback is not None
            and hour.boundary_layer_height is None
            and fallback.boundary_layer_height is not None
        ):
            merged.append(replace(hour, boundary_layer_height=fallback.boundary_layer_height))
            filled += 1
        else:
            merged.append(hour)

    if filled:
        return merged, f"Boundary layer height filled from {BOUNDARY_LAYER_MODEL}; primary surface model is {primary_model}."
    return hours, f"Boundary layer height unavailable from {primary_model}; {BOUNDARY_LAYER_MODEL} returned no matching boundary-layer data."


def fetch_profile(
    client: OpenMeteoClient,
    venue: Venue,
    race_area: RaceArea | None,
    forecast_date: str,
    target_hour: int,
) -> tuple[ForecastProfile | None, str | None]:
    latitude = race_area.latitude if race_area else venue.latitude
    longitude = race_area.longitude if race_area else venue.longitude
    try:
        profile = client.fetch_profile(
            latitude=latitude,
            longitude=longitude,
            timezone=venue.timezone,
            forecast_date=forecast_date,
            target_hour=target_hour,
            model=PROFILE_MODEL,
        )
    except Exception as exc:
        return None, f"ECMWF profile unavailable for sounding chart ({exc})."
    if not profile.levels:
        return None, "ECMWF profile unavailable for sounding chart; no pressure-level values returned."
    return profile, None


def build_geography_profile(venue: Venue, race_area: RaceArea | None) -> VenueGeographyProfile | None:
    profiles = [
        profile
        for profile in (
            build_terrain_profile(venue, race_area),
            build_osm_geography_profile(race_area),
        )
        if profile is not None
    ]
    if not profiles:
        return None
    summary: list[str] = []
    counts: dict[str, int] = {}
    impacts: list[GeographySectorImpact] = []
    for profile in profiles:
        summary.extend(profile.summary)
        counts.update(profile.feature_counts)
        impacts.extend(profile.sector_impacts)
    return VenueGeographyProfile(
        source="; ".join(profile.source for profile in profiles),
        radius_km=max(profile.radius_km for profile in profiles),
        summary=summary,
        feature_counts=counts,
        sector_impacts=impacts,
    )


def custom_venue(
    name: str,
    latitude: float,
    longitude: float,
    race_area_name: str = "Race area",
    race_radius_nm: float = 2.0,
    timezone: str = "auto",
) -> Venue:
    key = slugify(name) or f"custom_{latitude:.4f}_{longitude:.4f}"
    return Venue(
        key=key,
        name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        shoreline_axis_deg=0,
        notes=(),
        race_areas=(
            RaceArea(
                name=race_area_name,
                latitude=latitude,
                longitude=longitude,
                radius_nm=race_radius_nm,
                notes=(),
            ),
        ),
    )


def build_custom_forecast_html(
    name: str,
    latitude: float,
    longitude: float,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    race_area_name: str = "Race area",
    race_radius_nm: float = 2.0,
    event: EventMetadata | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> str:
    venue = custom_venue(
        name=name,
        latitude=latitude,
        longitude=longitude,
        race_area_name=race_area_name,
        race_radius_nm=race_radius_nm,
    )
    forecast = build_forecast_for_venue(
        venue=venue,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )
    return render_forecast_html(forecast)


def build_custom_forecast_result(
    name: str,
    latitude: float,
    longitude: float,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    race_area_name: str = "Race area",
    race_radius_nm: float = 2.0,
    event: EventMetadata | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> dict[str, object]:
    venue = custom_venue(
        name=name,
        latitude=latitude,
        longitude=longitude,
        race_area_name=race_area_name,
        race_radius_nm=race_radius_nm,
    )
    forecast = build_forecast_for_venue(
        venue=venue,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )
    return {
        "html": render_forecast_html(forecast),
        "wind_maps": wind_maps_payload(forecast.area_maps),
        "area_map_mode": forecast.area_map_mode,
        "area_grid_size": normalize_area_grid_size(area_grid_size),
        "forecast_days": normalize_forecast_days(forecast_days),
    }


def wind_maps_payload(area_maps: list[AreaForecastMap]) -> list[dict[str, object]]:
    return [
        {
            "hour": area_map.hour,
            "time_label": area_map.time_label,
            "points": [area_point_payload(point) for point in area_map.points],
        }
        for area_map in area_maps
    ]


def area_point_payload(point: AreaForecastPoint) -> dict[str, float | None]:
    return {
        "latitude": point.latitude,
        "longitude": point.longitude,
        "wind_direction_10m": point.wind_direction_10m,
        "wind_speed_10m": point.wind_speed_10m,
        "wind_gust_10m": point.wind_gust_10m,
        "cloud_cover": point.cloud_cover,
        "sea_level_pressure": point.sea_level_pressure,
    }


def build_custom_forecast_text(
    name: str,
    latitude: float,
    longitude: float,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    race_area_name: str = "Race area",
    race_radius_nm: float = 2.0,
    event: EventMetadata | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> str:
    venue = custom_venue(
        name=name,
        latitude=latitude,
        longitude=longitude,
        race_area_name=race_area_name,
        race_radius_nm=race_radius_nm,
    )
    forecast = build_forecast_for_venue(
        venue=venue,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )
    return render_forecast_text(forecast)


def build_forecast_text(
    venue_key: str,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    event: EventMetadata | None = None,
    race_area_name: str | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> str:
    forecast = build_forecast(
        venue_key=venue_key,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )
    return render_forecast_text(forecast)


def build_forecast_html(
    venue_key: str,
    forecast_date: str,
    start_hour: int,
    end_hour: int,
    event: EventMetadata | None = None,
    race_area_name: str | None = None,
    model: str = AUTO_PRIMARY_MODEL,
    compare_models: list[str] | None = None,
    area_map_mode: str = "barbs",
    area_grid_size: int = DEFAULT_AREA_GRID_SIZE,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> str:
    forecast = build_forecast(
        venue_key=venue_key,
        forecast_date=forecast_date,
        start_hour=start_hour,
        end_hour=end_hour,
        event=event,
        race_area_name=race_area_name,
        model=model,
        compare_models=compare_models,
        area_map_mode=area_map_mode,
        area_grid_size=area_grid_size,
        forecast_days=forecast_days,
    )
    return render_forecast_html(forecast)


def normalize_area_map_mode(value: str | None) -> str:
    if value == "streamlines":
        return "streamlines"
    return "barbs"


def normalize_area_grid_size(value: int | str | None) -> int:
    try:
        grid_size = int(value or DEFAULT_AREA_GRID_SIZE)
    except (TypeError, ValueError):
        return DEFAULT_AREA_GRID_SIZE
    if grid_size in {9, 15, 21}:
        return grid_size
    return DEFAULT_AREA_GRID_SIZE


def normalize_forecast_days(value: int | str | None) -> int:
    try:
        days = int(value or DEFAULT_FORECAST_DAYS)
    except (TypeError, ValueError):
        return DEFAULT_FORECAST_DAYS
    if days in {1, 2}:
        return days
    return DEFAULT_FORECAST_DAYS


def find_race_area(race_areas: tuple[RaceArea, ...], name: str | None) -> RaceArea | None:
    if not race_areas:
        return None
    if not name:
        return race_areas[0]
    normalized = name.casefold()
    for race_area in race_areas:
        if race_area.name.casefold() == normalized:
            return race_area
    available = ", ".join(area.name for area in race_areas)
    raise ValueError(f"Unknown race area '{name}'. Available race areas: {available}")


def venue_payload() -> list[dict[str, object]]:
    return [
        {
            "key": venue.key,
            "name": venue.name,
            "latitude": venue.latitude,
            "longitude": venue.longitude,
            "timezone": venue.timezone,
            "default_models": list(venue.default_models),
            "race_areas": [
                {
                    "name": area.name,
                    "latitude": area.latitude,
                    "longitude": area.longitude,
                    "radius_nm": area.radius_nm,
                    "notes": list(area.notes),
                }
                for area in venue.race_areas
            ],
        }
        for venue in VENUES.values()
    ]


def slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_")
