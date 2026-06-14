from __future__ import annotations

from statistics import mean, pstdev

from sailing_forecast.models import AreaForecastMap, AreaForecastPoint, EventMetadata, ForecastHour, ForecastProfile, ModelForecastRun, RaceArea, SailingForecast, SailingHour, Venue, VenueGeographyProfile
from sailing_forecast.weather_math import angular_difference, circular_mean, clamp, rounded_direction


def analyze_forecast(
    venue: Venue,
    event: EventMetadata,
    race_area: RaceArea | None,
    forecast_date: str,
    forecast_hours: list[ForecastHour],
    start_hour: int,
    end_hour: int,
    model_name: str,
    model_summaries: list[str] | None = None,
    model_runs: list[ModelForecastRun] | None = None,
    area_points: list[AreaForecastPoint] | None = None,
    area_map_time: str | None = None,
    area_maps: list[AreaForecastMap] | None = None,
    area_map_mode: str = "barbs",
    geography_profile: VenueGeographyProfile | None = None,
    profile: ForecastProfile | None = None,
) -> SailingForecast:
    race_hours = [hour for hour in forecast_hours if start_hour <= hour.time.hour <= end_hour]
    if not race_hours:
        raise ValueError("No forecast data found for the requested race window.")

    model_runs = model_runs or []
    executive_hours, executive_model = executive_source_hours(model_runs, race_hours)
    include_date_label = len({hour.time.date() for hour in race_hours}) > 1
    sailing_hours = [_analyze_hour(hour, include_date_label) for hour in race_hours]
    executive_sailing_hours = [_analyze_hour(hour, include_date_label) for hour in executive_hours]
    type_of_day = _type_of_day(race_hours)
    confidence = _confidence(race_hours)
    summary = _summary(type_of_day, executive_sailing_hours, executive_hours, executive_model)
    meteorology = _meteorology(race_hours, area_maps or [])
    local_effects = _local_effects(venue, race_area, race_hours, geography_profile)
    marine_summary = _marine_summary(race_hours)

    return SailingForecast(
        venue=venue,
        event=event,
        race_area=race_area,
        forecast_date=forecast_date,
        race_window=f"{start_hour:02d}00-{end_hour:02d}00 local",
        model_name=model_name,
        type_of_day=type_of_day,
        confidence=confidence,
        executive_summary=summary,
        meteorology=meteorology,
        local_effects=local_effects,
        geography_profile=geography_profile,
        hours=sailing_hours,
        source_hours=race_hours,
        area_points=area_points or [],
        area_map_time=area_map_time,
        area_maps=area_maps or [],
        area_map_mode=area_map_mode,
        model_summaries=model_summaries or [],
        marine_summary=marine_summary,
        model_runs=model_runs,
        profile=profile,
    )


def _analyze_hour(hour: ForecastHour, include_date_label: bool = False) -> SailingHour:
    mean_dir = rounded_direction(hour.wind_direction_10m)
    gust_delta = max(1.0, hour.wind_gust_10m - hour.wind_speed_10m)
    cloud = hour.cloud_cover or 0
    instability = 1 if (hour.cape or 0) > 100 else 0
    spread = clamp(6 + gust_delta * 1.6 + cloud / 18 + instability * 4, 8, 28)
    lull_delta = clamp(gust_delta * 0.55 + cloud / 35, 1, 8)
    speed_spread = clamp(gust_delta * 0.55 + cloud / 45, 1.5, 5.5)

    return SailingHour(
        time_label=hour.time.strftime("%m-%d %H%M") if include_date_label else hour.time.strftime("%H%M"),
        twd_mean=mean_dir,
        twd_min=rounded_direction(mean_dir - spread, 5),
        twd_max=rounded_direction(mean_dir + spread, 5),
        tws_mean=round(hour.wind_speed_10m),
        tws_min=max(0, round(hour.wind_speed_10m - speed_spread)),
        tws_max=round(hour.wind_speed_10m + speed_spread),
        gust=round(hour.wind_gust_10m),
        lull=max(0, round(hour.wind_speed_10m - lull_delta)),
        phase=_phase(hour, gust_delta, spread),
        note=_hour_note(hour, gust_delta),
    )


def _phase(hour: ForecastHour, gust_delta: float, spread: float) -> str:
    if hour.wind_speed_10m < 6:
        return "patchy"
    if spread > 20:
        return "shifty"
    if gust_delta >= 5:
        return "gust-led"
    if hour.wind_direction_925hpa is not None:
        diff = angular_difference(hour.wind_direction_10m, hour.wind_direction_925hpa)
        if diff > 35:
            return "thermal bend"
    return "steady"


def _hour_note(hour: ForecastHour, gust_delta: float) -> str:
    notes: list[str] = []
    if hour.wind_direction_925hpa is not None:
        diff = angular_difference(hour.wind_direction_10m, hour.wind_direction_925hpa)
        if diff > 35:
            notes.append("surface breeze is bent away from gradient")
    if (hour.cloud_cover or 0) > 60:
        notes.append("cloud may soften pressure")
    if gust_delta >= 5:
        notes.append("noticeable gust-lull spread")
    if hour.wind_speed_10m < 6:
        notes.append("look for pressure patches")
    return "; ".join(notes) if notes else "normal phase range"


def _type_of_day(hours: list[ForecastHour]) -> str:
    avg_speed = mean(hour.wind_speed_10m for hour in hours)
    avg_cloud = mean((hour.cloud_cover or 0) for hour in hours)
    avg_radiation = mean((hour.shortwave_radiation or 0) for hour in hours)
    thermal_turn = _thermal_turn_signal(hours)
    gradient_gap = _mean_gradient_gap(hours)

    if avg_speed < 6 and avg_radiation > 350:
        return "light thermal / patchy pressure day"
    if thermal_turn > 25 and gradient_gap > 25:
        return "thermal-bend day over a separate gradient"
    if avg_cloud > 65:
        return "cloud-modulated gradient day"
    if avg_speed >= 14 and gradient_gap < 25:
        return "gradient-dominant day"
    return "mixed gradient and thermal day"


def _confidence(hours: list[ForecastHour]) -> str:
    direction_std = pstdev(hour.wind_direction_10m for hour in hours) if len(hours) > 1 else 0
    avg_cloud = mean((hour.cloud_cover or 0) for hour in hours)
    avg_speed = mean(hour.wind_speed_10m for hour in hours)
    score = 8
    if direction_std > 25:
        score -= 2
    if avg_cloud > 60:
        score -= 1
    if avg_speed < 6:
        score -= 2
    if _thermal_turn_signal(hours) > 35:
        score -= 1
    label = "high" if score >= 7 else "moderate" if score >= 5 else "low"
    return f"{label} ({score}/10)"


def executive_source_hours(
    model_runs: list[ModelForecastRun],
    fallback_hours: list[ForecastHour],
) -> tuple[list[ForecastHour], str | None]:
    if not model_runs:
        return fallback_hours, None
    preferred_order = (
        "ukmo_uk_deterministic_2km",
        "meteofrance_arome_france_hd",
        "meteofrance_arome_france",
        "meteofrance_arpege_europe",
        "ukmo_global_deterministic_10km",
        "meteofrance_arpege_world",
        "ecmwf_ifs025",
        "icon_global",
        "ecmwf_ifs04",
        "gfs_seamless",
    )
    for model_name in preferred_order:
        for run in model_runs:
            if run.name == model_name and run.hours:
                return run.hours, run.name
    first = next((run for run in model_runs if run.hours), None)
    if first:
        return first.hours, first.name
    return fallback_hours, None


def _summary(type_of_day: str, sailing_hours: list[SailingHour], hours: list[ForecastHour], model_name: str | None = None) -> str:
    start = sailing_hours[0]
    end = sailing_hours[-1]
    avg_gust_delta = mean(hour.wind_gust_10m - hour.wind_speed_10m for hour in hours)
    trend = "building" if end.tws_mean > start.tws_mean + 2 else "easing" if end.tws_mean < start.tws_mean - 2 else "fairly level"
    bend = _direction_trend(start.twd_mean, end.twd_mean)
    source = f" using {model_name}" if model_name else ""
    return (
        f"{type_of_day.capitalize()}{source}. Breeze starts around {start.twd_mean:03d} at "
        f"{start.tws_mean} kt and finishes around {end.twd_mean:03d} at {end.tws_mean} kt; "
        f"speed trend is {trend}, direction trend is {bend}. Expected gust-lull delta is "
        f"about {round(avg_gust_delta)} kt, with the largest tactical value in pressure differences "
        f"when the breeze is under 8 kt or cloud increases."
    )


def _meteorology(hours: list[ForecastHour], area_maps: list[AreaForecastMap] | None = None) -> list[str]:
    avg_surface_dir = circular_mean([hour.wind_direction_10m for hour in hours])
    avg_surface_speed = mean(hour.wind_speed_10m for hour in hours)
    gradient_hours = [hour for hour in hours if hour.wind_direction_925hpa is not None and hour.wind_speed_925hpa is not None]
    avg_cloud = mean((hour.cloud_cover or 0) for hour in hours)
    avg_bl = mean((hour.boundary_layer_height or 0) for hour in hours)
    avg_cape = mean((hour.cape or 0) for hour in hours)

    bullets = [
        f"Surface flow averages {rounded_direction(avg_surface_dir):03d} at {round(avg_surface_speed)} kt through the race window.",
        f"Cloud cover averages {round(avg_cloud)}%, so cloud impact is {'material' if avg_cloud > 55 else 'limited'}.",
        f"Boundary layer height averages about {round(avg_bl)} m; mixing potential is {'good' if avg_bl > 700 else 'shallow to moderate'}.",
    ]
    bullets.extend(_thermal_and_pressure_diagnostics(hours, area_maps or []))
    if gradient_hours:
        avg_grad_dir = circular_mean([hour.wind_direction_925hpa or 0 for hour in gradient_hours])
        avg_grad_speed = mean(hour.wind_speed_925hpa or 0 for hour in gradient_hours)
        gap = angular_difference(avg_surface_dir, avg_grad_dir)
        bullets.insert(
            1,
            f"925 hPa gradient averages {rounded_direction(avg_grad_dir):03d} at {round(avg_grad_speed)} kt; surface-gradient separation is about {round(gap)} degrees.",
        )
    if avg_cape > 100:
        bullets.append("CAPE is high enough to increase gust and cloud-line uncertainty.")
    else:
        bullets.append("CAPE is low, so gusts should mostly come from mixing, terrain and pressure patches rather than deep convection.")
    return bullets


def _thermal_and_pressure_diagnostics(hours: list[ForecastHour], area_maps: list[AreaForecastMap]) -> list[str]:
    bullets: list[str] = []
    temperature_hours = [hour for hour in hours if hour.temperature_2m is not None]
    sst_hours = [hour for hour in hours if hour.sea_surface_temperature is not None]
    radiation_hours = [hour for hour in hours if hour.shortwave_radiation is not None]
    pressure_hours = [hour for hour in hours if hour.sea_level_pressure is not None]

    if temperature_hours and sst_hours:
        avg_air = mean(hour.temperature_2m or 0 for hour in temperature_hours)
        avg_sst = mean(hour.sea_surface_temperature or 0 for hour in sst_hours)
        contrast = avg_air - avg_sst
        if contrast >= 3:
            contrast_note = "supports a thermally driven onshore component if the gradient allows it"
        elif contrast <= -1:
            contrast_note = "favours stable marine air and weaker thermal mixing"
        else:
            contrast_note = "is modest, so thermal forcing is not dominant by itself"
        bullets.append(f"Air-SST contrast averages {contrast:+.1f} C ({avg_air:.1f} C air vs {avg_sst:.1f} C sea); {contrast_note}.")

    if len(hours) >= 2:
        cloud_start = hours[0].cloud_cover or 0
        cloud_end = hours[-1].cloud_cover or 0
        cloud_change = cloud_end - cloud_start
        radiation = mean(hour.shortwave_radiation or 0 for hour in radiation_hours) if radiation_hours else 0
        trend = "increasing" if cloud_change > 15 else "clearing" if cloud_change < -15 else "fairly steady"
        bullets.append(
            f"Cloud trend is {trend} ({round(cloud_start)}% to {round(cloud_end)}%) with mean shortwave radiation around {round(radiation)} W/m2."
        )

    if len(pressure_hours) >= 2:
        pressure_change = (pressure_hours[-1].sea_level_pressure or 0) - (pressure_hours[0].sea_level_pressure or 0)
        tendency = "rising" if pressure_change > 0.7 else "falling" if pressure_change < -0.7 else "near steady"
        bullets.append(f"MSLP tendency is {tendency}, changing {pressure_change:+.1f} hPa across the race window.")

    pressure_spread = area_pressure_spread_change(area_maps)
    if pressure_spread is not None:
        start_label, start_spread, end_label, end_spread = pressure_spread
        change = end_spread - start_spread
        gradient_note = "tightening" if change > 0.2 else "relaxing" if change < -0.2 else "little changed"
        bullets.append(
            f"Race-area pressure spread is {gradient_note}: {start_spread:.1f} hPa at {start_label} to {end_spread:.1f} hPa at {end_label}."
        )

    score, reason = sea_breeze_potential(hours)
    bullets.append(f"Sea-breeze potential score is {score}/10: {reason}")
    return bullets


def area_pressure_spread_change(area_maps: list[AreaForecastMap]) -> tuple[str, float, str, float] | None:
    spreads: list[tuple[str, float]] = []
    for area_map in area_maps:
        pressures = [
            point.sea_level_pressure
            for point in area_map.points
            if point.sea_level_pressure is not None
        ]
        if len(pressures) >= 2:
            spreads.append((area_map.time_label, max(pressures) - min(pressures)))
    if len(spreads) < 2:
        return None
    start_label, start_spread = spreads[0]
    end_label, end_spread = spreads[-1]
    return start_label, start_spread, end_label, end_spread


def sea_breeze_potential(hours: list[ForecastHour]) -> tuple[int, str]:
    avg_speed = mean(hour.wind_speed_10m for hour in hours)
    avg_cloud = mean((hour.cloud_cover or 0) for hour in hours)
    avg_bl = mean((hour.boundary_layer_height or 0) for hour in hours)
    avg_radiation = mean((hour.shortwave_radiation or 0) for hour in hours)
    thermal_turn = _thermal_turn_signal(hours)
    temperature_hours = [hour for hour in hours if hour.temperature_2m is not None and hour.sea_surface_temperature is not None]
    air_sst_contrast = mean((hour.temperature_2m or 0) - (hour.sea_surface_temperature or 0) for hour in temperature_hours) if temperature_hours else 0

    score = 0
    reasons: list[str] = []
    if air_sst_contrast >= 4:
        score += 3
        reasons.append("warm air over cooler sea")
    elif air_sst_contrast >= 2:
        score += 2
        reasons.append("some land-sea thermal contrast")
    elif air_sst_contrast >= 0.5:
        score += 1
        reasons.append("weak thermal contrast")

    if avg_radiation >= 550:
        score += 3
        reasons.append("strong solar input")
    elif avg_radiation >= 300:
        score += 2
        reasons.append("usable solar input")
    elif avg_radiation >= 150:
        score += 1
        reasons.append("limited solar input")

    if avg_cloud <= 35:
        score += 2
        reasons.append("low cloud cover")
    elif avg_cloud <= 60:
        score += 1
        reasons.append("partial cloud")

    if 4 <= avg_speed <= 12:
        score += 1
        reasons.append("gradient is light to moderate")
    elif avg_speed > 16:
        reasons.append("stronger gradient may suppress a separate sea breeze")

    if avg_bl >= 600:
        score += 1
        reasons.append("boundary layer can mix")
    if thermal_turn >= 20:
        score += 1
        reasons.append("forecast already shows a thermal-style direction turn")

    score = int(clamp(score, 0, 10))
    if not reasons:
        reasons.append("weak thermal signal in the available fields")
    return score, ", ".join(reasons) + "."


def _local_effects(
    venue: Venue,
    race_area: RaceArea | None,
    hours: list[ForecastHour],
    geography_profile: VenueGeographyProfile | None = None,
) -> list[str]:
    effects = venue_notes_for_effects(venue, geography_profile)
    if race_area:
        effects.append(f"Race area: {race_area.name}, centered near {race_area.latitude:.3f}, {race_area.longitude:.3f}, radius about {race_area.radius_nm:g} nm.")
        effects.extend(race_area_notes_for_effects(race_area, geography_profile))
    avg_dir = circular_mean([hour.wind_direction_10m for hour in hours])
    if venue.sector_rules:
        shoreline_angle = angular_difference(avg_dir, venue.shoreline_axis_deg)
        if shoreline_angle < 25 or shoreline_angle > 155:
            effects.append("Flow is close to the shoreline axis, so small coastal bends and acceleration zones may matter.")
        else:
            effects.append("Flow is more cross-shore, so land-water heating contrast is likely more important than shoreline channeling.")
    elif geography_profile:
        effects.append("DEM/OSM geography is available for this custom venue; shoreline rules are still provisional until classified separately.")
    else:
        effects.append("No venue-specific shoreline or topographic rules are configured yet; treat local-effect notes as provisional.")
    for rule in venue.sector_rules:
        if _direction_in_sector(avg_dir, rule.start_deg, rule.end_deg):
            effects.append(f"{rule.name}: " + " ".join(rule.notes))
    if geography_profile:
        effects.extend(geography_profile.summary)
        matching_impacts = [
            impact
            for impact in geography_profile.sector_impacts
            if _direction_in_named_sector(avg_dir, impact.sector)
        ]
        for impact in matching_impacts:
            effects.append(f"Mean wind sector geography check: {impact.note}")
    return effects


def venue_notes_for_effects(venue: Venue, geography_profile: VenueGeographyProfile | None) -> list[str]:
    if geography_profile is None:
        return list(venue.notes)
    generic_fragments = (
        "Local geography has not been classified yet",
        "Use observations and visual checks to refine shoreline",
    )
    return [
        note
        for note in venue.notes
        if not any(fragment in note for fragment in generic_fragments)
    ]


def race_area_notes_for_effects(race_area: RaceArea, geography_profile: VenueGeographyProfile | None) -> list[str]:
    if geography_profile is None:
        return list(race_area.notes)
    generic_fragments = (
        "Race area generated from the map-selected venue point",
        "Move or tune this once course geometry is known",
    )
    return [
        note
        for note in race_area.notes
        if not any(fragment in note for fragment in generic_fragments)
    ]


def _marine_summary(hours: list[ForecastHour]) -> str | None:
    wave_hours = [hour for hour in hours if hour.wave_height is not None]
    if not wave_hours:
        return None
    avg_wave = mean(hour.wave_height or 0 for hour in wave_hours)
    avg_period = mean(hour.wave_period or 0 for hour in wave_hours if hour.wave_period is not None)
    avg_dir = circular_mean([hour.wave_direction or 0 for hour in wave_hours if hour.wave_direction is not None])
    return f"Sea state: mean wave height around {avg_wave:.1f} m from {rounded_direction(avg_dir):03d}, period about {avg_period:.0f} s."


def _thermal_turn_signal(hours: list[ForecastHour]) -> float:
    return angular_difference(hours[0].wind_direction_10m, hours[-1].wind_direction_10m)


def _mean_gradient_gap(hours: list[ForecastHour]) -> float:
    gaps = [
        angular_difference(hour.wind_direction_10m, hour.wind_direction_925hpa)
        for hour in hours
        if hour.wind_direction_925hpa is not None
    ]
    return mean(gaps) if gaps else 0


def _direction_trend(start: int, end: int) -> str:
    diff = (end - start + 540) % 360 - 180
    if diff > 10:
        return f"veering right by {round(diff)} degrees"
    if diff < -10:
        return f"backing left by {round(abs(diff))} degrees"
    return "mostly oscillatory with little net trend"


def _direction_in_sector(direction: float, start: int, end: int) -> bool:
    direction %= 360
    start %= 360
    end %= 360
    if start <= end:
        return start <= direction <= end
    return direction >= start or direction <= end


def _direction_in_named_sector(direction: float, sector: str) -> bool:
    sectors = {
        "N": (337.5, 22.5),
        "NE": (22.5, 67.5),
        "E": (67.5, 112.5),
        "SE": (112.5, 157.5),
        "S": (157.5, 202.5),
        "SW": (202.5, 247.5),
        "W": (247.5, 292.5),
        "NW": (292.5, 337.5),
    }
    bounds = sectors.get(sector)
    if bounds is None:
        return False
    return _direction_in_sector(direction, bounds[0], bounds[1])
