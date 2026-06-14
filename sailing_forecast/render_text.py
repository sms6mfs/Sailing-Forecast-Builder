from __future__ import annotations

from sailing_forecast.models import SailingForecast


def render_forecast_text(forecast: SailingForecast) -> str:
    lines = [
        f"Sailing Forecast - {forecast.venue.name}",
        f"Event: {forecast.event.name}",
        f"Team: {forecast.event.team or 'n/a'}",
        f"Forecaster: {forecast.event.forecaster}",
        f"Issue time: {forecast.event.issue_time or 'n/a'}",
        f"Date: {forecast.forecast_date}",
        f"Race window: {forecast.race_window}",
        f"Race area: {forecast.race_area.name if forecast.race_area else 'n/a'}",
        f"Primary model: {forecast.model_name}",
        f"Synoptic chart: {forecast.event.synoptic_chart_url or 'n/a'}",
        f"Type of day: {forecast.type_of_day}",
        f"Confidence: {forecast.confidence}",
        "",
        "Executive brief",
        forecast.executive_summary,
        "",
        "Hourly sailing wind",
        "Time  TWD range  TWS range  Gust  Lull  Phase         Notes",
    ]
    for hour in forecast.hours:
        lines.append(
            f"{hour.time_label}  {hour.twd_mean:03d} ({hour.twd_min:03d}-{hour.twd_max:03d})  "
            f"{hour.tws_mean:>2} ({hour.tws_min:>2}-{hour.tws_max:>2})    "
            f"{hour.gust:>2}    {hour.lull:>2}   {hour.phase:<12} {hour.note}"
        )

    lines.extend(["", "Meteorology"])
    lines.extend(f"- {item}" for item in forecast.meteorology)
    if forecast.model_summaries:
        lines.extend(["", "Model comparison"])
        lines.extend(f"- {item}" for item in forecast.model_summaries)
    lines.extend(["", "Local effects"])
    lines.extend(f"- {item}" for item in forecast.local_effects)

    if forecast.marine_summary:
        lines.extend(["", forecast.marine_summary])

    return "\n".join(lines)
