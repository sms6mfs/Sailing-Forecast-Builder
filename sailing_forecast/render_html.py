from __future__ import annotations

import math
from html import escape
from urllib.parse import urlparse

from sailing_forecast.models import AreaForecastMap, AreaForecastPoint, ForecastHour, ForecastProfile, ModelForecastRun, SailingForecast
from sailing_forecast.weather_math import angular_difference


def render_forecast_html(forecast: SailingForecast) -> str:
    issued = forecast.source_hours[0].time.strftime("%Y-%m-%d") if forecast.source_hours else forecast.forecast_date
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{escape(forecast.venue.name)} Sailing Forecast</title>
  <style>
    :root {{
      --ink: #172027;
      --muted: #5a6670;
      --line: #d8e0e5;
      --panel: #f6f8f9;
      --blue: #1e6a8d;
      --teal: #1d7b72;
      --gold: #b77812;
      --red: #b84b42;
    }}
    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #eef3f5;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.35;
    }}
    .page {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px;
      background: white;
      min-height: 100vh;
    }}
    header {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 18px;
      border-bottom: 3px solid var(--ink);
      padding-bottom: 16px;
      margin-bottom: 18px;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 30px; margin-bottom: 6px; letter-spacing: 0; }}
    h2 {{ font-size: 17px; margin-bottom: 10px; }}
    h3 {{ font-size: 14px; margin-bottom: 7px; color: var(--muted); text-transform: uppercase; }}
    .meta {{
      display: grid;
      gap: 4px;
      color: var(--muted);
      font-size: 13px;
      text-align: right;
    }}
    .brief {{
      display: grid;
      grid-template-columns: 1.8fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .band, .panel {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      background: var(--panel);
    }}
    .band {{
      border-left: 6px solid var(--blue);
      background: #ffffff;
    }}
    .facts {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}
    .fact {{
      border-left: 4px solid var(--teal);
      padding-left: 10px;
    }}
    .fact b {{
      display: block;
      font-size: 20px;
    }}
    .fact span {{
      color: var(--muted);
      font-size: 12px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      margin-bottom: 18px;
    }}
    th {{
      text-align: left;
      background: var(--ink);
      color: white;
      padding: 7px 8px;
      font-weight: 700;
    }}
    td {{
      border-bottom: 1px solid var(--line);
      padding: 7px 8px;
      vertical-align: top;
    }}
    td.num {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{ margin-bottom: 7px; }}
    .charts {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 18px;
    }}
    .chart svg {{
      width: 100%;
      height: auto;
      display: block;
      background: white;
      border: 1px solid var(--line);
      border-radius: 4px;
    }}
    .panel svg {{
      width: 100%;
      height: auto;
      display: block;
      background: white;
      border: 1px solid var(--line);
      border-radius: 4px;
    }}
    .wind-map-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    .wind-map h3 {{
      margin-bottom: 6px;
      color: var(--ink);
      text-transform: none;
      font-size: 14px;
    }}
    .tile-map {{
      position: relative;
      width: 100%;
      max-width: 768px;
      aspect-ratio: 1;
      margin: 0 auto;
      overflow: hidden;
      background: #d8e0e5;
      border: 2px solid var(--ink);
      border-radius: 4px;
    }}
    .tile-map img {{
      position: absolute;
      width: 33.3334%;
      height: 33.3334%;
      object-fit: cover;
    }}
    .tile-map .venue-dot {{
      position: absolute;
      width: 14px;
      height: 14px;
      margin-left: -7px;
      margin-top: -7px;
      border: 3px solid #ffffff;
      border-radius: 50%;
      background: var(--red);
      box-shadow: 0 0 0 2px var(--ink);
      z-index: 4;
    }}
    .tile-map .race-radius {{
      position: absolute;
      border: 3px solid var(--blue);
      border-radius: 50%;
      background: rgba(30, 106, 141, 0.12);
      z-index: 3;
      transform: translate(-50%, -50%);
    }}
    .tile-map .wind-overlay {{
      position: absolute;
      inset: 0;
      z-index: 5;
      width: 100%;
      height: 100%;
      background: transparent !important;
      border: 0 !important;
      pointer-events: none;
    }}
    .forecast-tile-map {{
      max-width: 520px;
    }}
    .map-caption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .synoptic-source {{
      display: inline-block;
      color: var(--blue);
      font-weight: 700;
      word-break: break-word;
    }}
    .synoptic-image {{
      width: 100%;
      max-height: 560px;
      object-fit: contain;
      background: white;
      border: 1px solid var(--line);
      border-radius: 4px;
    }}
    .legend {{
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 12px;
      margin-top: 6px;
    }}
    .swatch {{
      display: inline-block;
      width: 18px;
      height: 3px;
      margin-right: 5px;
      vertical-align: middle;
      background: var(--blue);
    }}
    .speed-cell {{
      font-weight: 700;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    footer {{
      color: var(--muted);
      font-size: 11px;
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }}
    .print-page {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .print-break-before {{
      break-before: page;
      page-break-before: always;
    }}
    .print-avoid {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    @media print {{
      @page {{ size: A4; margin: 8mm; }}
      html, body {{
        width: 210mm;
        background: white;
      }}
      body {{
        font-size: 10px;
        line-height: 1.18;
      }}
      .page {{
        max-width: none;
        padding: 0;
        min-height: auto;
      }}
      header {{
        grid-template-columns: 1fr auto;
        gap: 8px;
        padding-bottom: 7px;
        margin-bottom: 8px;
        border-bottom-width: 2px;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      h1 {{ font-size: 20px; margin-bottom: 2px; }}
      h2 {{ font-size: 12px; margin-bottom: 5px; }}
      h3 {{ font-size: 10px; margin-bottom: 3px; }}
      p {{ margin-bottom: 0; }}
      .meta {{ font-size: 8.5px; gap: 1px; }}
      .brief {{
        grid-template-columns: 1.9fr 1fr;
        gap: 8px;
        margin-bottom: 8px;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      .band, .panel {{
        border-radius: 4px;
        padding: 7px;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      .band {{ border-left-width: 4px; }}
      .facts {{ gap: 6px; }}
      .fact {{ border-left-width: 3px; padding-left: 6px; }}
      .fact b {{ font-size: 14px; }}
      .fact span {{ font-size: 8px; }}
      section {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      table {{
        font-size: 8px;
        margin-bottom: 7px;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      th, td {{
        padding: 3px 4px;
      }}
      thead {{
        display: table-header-group;
      }}
      tr {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      ul {{ padding-left: 12px; }}
      li {{ margin-bottom: 3px; }}
      .synoptic-image {{
        max-height: 96mm;
      }}
      .charts {{
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 6px;
      }}
      .chart {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      .chart svg {{
        max-height: 44mm;
      }}
      .grid-2 {{
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        margin-bottom: 6px;
      }}
      .wind-map-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 4px 6px;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      .wind-map {{
        break-inside: avoid;
        page-break-inside: avoid;
        min-width: 0;
      }}
      .wind-map h3 {{
        font-size: 9px;
        margin-bottom: 2px;
      }}
      .forecast-tile-map {{
        width: 100%;
        max-width: 86mm;
      }}
      .tile-map {{
        border-width: 1px;
        aspect-ratio: 1 / 1;
      }}
      .forecast-map-section .tile-map {{
        width: 100%;
        max-height: 86mm;
      }}
      .forecast-map-section .wind-overlay {{
        max-height: 86mm;
      }}
      .map-caption {{
        margin-top: 4px;
        font-size: 8px;
      }}
      .legend {{
        gap: 7px;
        font-size: 8px;
        margin-top: 2px;
      }}
      .print-page + .print-page {{
        padding-top: 0;
      }}
      .print-compact-panel {{
        padding: 5px;
      }}
      .print-compact-panel li {{
        margin-bottom: 2px;
      }}
      .profile-section svg {{
        max-height: 82mm;
      }}
      .forecast-map-section {{
        margin-bottom: 6px !important;
      }}
      footer {{
        font-size: 8px;
        padding-top: 5px;
      }}
    }}
    @media screen and (max-width: 800px) {{
      .page {{ padding: 18px; }}
      header, .brief, .grid-2, .charts, .wind-map-grid {{ grid-template-columns: 1fr; }}
      .meta {{ text-align: left; }}
      .facts {{ grid-template-columns: 1fr; }}
      table {{ font-size: 12px; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <div class="print-page">
      <header>
        <div>
          <h1>{escape(forecast.event.name)}</h1>
          <p>{escape(forecast.venue.name)} - {escape(forecast.type_of_day.capitalize())}</p>
        </div>
        <div class="meta">
          <div>Team: {escape(forecast.event.team or "n/a")}</div>
          <div>Forecaster: {escape(forecast.event.forecaster)}</div>
          <div>Issue: {escape(forecast.event.issue_time or issued)}</div>
          <div>Date: {escape(forecast.forecast_date)}</div>
          <div>Race window: {escape(forecast.race_window)}</div>
          <div>Race area: {escape(forecast.race_area.name if forecast.race_area else "n/a")}</div>
          <div>Primary model: {escape(forecast.model_name)}</div>
          <div>Confidence: {escape(forecast.confidence)}</div>
          <div>Source: Open-Meteo forecast and marine APIs</div>
        </div>
      </header>

      <section class="brief">
        <div class="band">
          <h2>Executive Brief</h2>
          <p>{escape(forecast.executive_summary)}</p>
        </div>
        <div class="panel">
          <h2>Key Numbers</h2>
          {render_key_facts(forecast)}
        </div>
      </section>

      {render_synoptic_chart_section(forecast)}

      <section class="print-avoid">
        <h2>925 hPa Wind</h2>
        {render_925_table(forecast)}
      </section>

      <section class="print-avoid">
        <h2>Hourly Sailing Wind</h2>
        {render_hour_table(forecast)}
      </section>
    </div>

    <div class="print-page print-break-before">
      <section class="panel forecast-map-section">
        <h2>Forecast Area Wind Maps</h2>
        {render_forecast_area_maps(forecast)}
      </section>

      <section class="charts">
        <div class="chart">
          <h2>Wind Speed By Model</h2>
          {line_chart(forecast, "speed")}
          {chart_legend(forecast, "speed")}
        </div>
        <div class="chart">
          <h2>Wind Direction By Model</h2>
          {line_chart(forecast, "direction")}
          {chart_legend(forecast, "direction")}
        </div>
        <div class="chart">
          <h2>Cloud And Boundary Layer</h2>
          {line_chart(forecast, "cloud")}
          <div class="legend">
            <span><span class="swatch" style="background: var(--blue)"></span>Cloud %</span>
            <span><span class="swatch" style="background: var(--teal)"></span>Boundary layer</span>
          </div>
        </div>
        <div class="chart">
          <h2>Sea State</h2>
          {line_chart(forecast, "marine")}
          <div class="legend">
            <span><span class="swatch" style="background: var(--blue)"></span>Wave height</span>
          </div>
        </div>
      </section>
      <section class="grid-2">
        <div class="panel print-compact-panel">
          <h2>Meteorology</h2>
          {render_list(forecast.meteorology)}
        </div>
        <div class="panel print-compact-panel">
          <h2>Venue Effects</h2>
          {render_list(forecast.local_effects)}
        </div>
      </section>

      {render_model_section(forecast)}

      {render_profile_section(forecast)}
    </div>

    <footer>
      Generated for planning and race briefing. Forecast date resolved from local venue time. {escape(forecast.marine_summary or "")}
    </footer>
  </main>
</body>
</html>
"""


def render_key_facts(forecast: SailingForecast) -> str:
    speeds = [hour.tws_mean for hour in forecast.hours]
    gusts = [hour.gust for hour in forecast.hours]
    directions = [hour.twd_mean for hour in forecast.hours]
    shift = angular_difference(directions[0], directions[-1]) if len(directions) >= 2 else 0
    return f"""
        <div class="facts">
          <div class="fact"><b>{min(speeds)}-{max(speeds)} kt</b><span>Mean wind range</span></div>
          <div class="fact"><b>{max(gusts)} kt</b><span>Peak forecast gust</span></div>
          <div class="fact"><b>{round(shift)} deg</b><span>Net direction change</span></div>
        </div>
    """


def render_925_table(forecast: SailingForecast) -> str:
    target_hours = [11, 13, 15, 17]
    directions = []
    speeds = []
    for target_hour in target_hours:
        source = closest_source_hour(forecast.source_hours, target_hour)
        if source is None:
            directions.append("n/a")
            speeds.append("n/a")
            continue
        direction = "n/a" if source.wind_direction_925hpa is None else f"{round(source.wind_direction_925hpa):03d}"
        speed = None if source.wind_speed_925hpa is None else source.wind_speed_925hpa
        directions.append(direction)
        speeds.append(speed)
    header_cells = "".join(f"<th>{target_hour:02d}:00 local</th>" for target_hour in target_hours)
    direction_cells = "".join(f'<td class="num">{direction}</td>' for direction in directions)
    speed_cells = "".join(speed_cell(speed) for speed in speeds)
    return (
        "<table>"
        f"<thead><tr><th>Time</th>{header_cells}</tr></thead>"
        f"<tbody><tr><th>925 hPa TWD</th>{direction_cells}</tr>"
        f"<tr><th>925 hPa TWS</th>{speed_cells}</tr></tbody></table>"
    )


def closest_source_hour(hours: list[ForecastHour], target_hour: int) -> ForecastHour | None:
    if not hours:
        return None
    return min(hours, key=lambda hour: abs(hour.time.hour - target_hour))


def speed_cell(speed: float | int | None) -> str:
    if speed is None:
        return '<td class="num">n/a</td>'
    value = round(speed)
    background = wind_speed_colour(float(speed), 0, 0)
    color = wind_speed_text_colour(float(speed))
    return f'<td class="num speed-cell" style="background-color:{background} !important; color:{color} !important;">{value} kt</td>'


def speed_range_cell(low: float | int, high: float | int) -> str:
    average = (float(low) + float(high)) / 2
    background = wind_speed_colour(average, 0, 0)
    color = wind_speed_text_colour(average)
    return f'<td class="num speed-cell" style="background-color:{background} !important; color:{color} !important;">{round(low)}-{round(high)} kt</td>'


def render_hour_table(forecast: SailingForecast) -> str:
    rows = []
    for hour in forecast.hours:
        rows.append(
            "<tr>"
            f"<td class=\"num\">{hour.time_label}</td>"
            f"<td class=\"num\">{hour.twd_mean:03d}</td>"
            f"<td class=\"num\">{hour.twd_min:03d}-{hour.twd_max:03d}</td>"
            f"{speed_cell(hour.tws_mean)}"
            f"{speed_range_cell(hour.tws_min, hour.tws_max)}"
            f"{speed_cell(hour.gust)}"
            f"{speed_cell(hour.lull)}"
            f"<td>{escape(hour.phase)}</td>"
            f"<td>{escape(hour.note)}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<thead><tr><th>Time</th><th>TWD</th><th>TWD range</th><th>TWS</th><th>TWS range</th>"
        "<th>Gust</th><th>Lull</th><th>Phase</th><th>Notes</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def render_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def render_model_section(forecast: SailingForecast) -> str:
    if not forecast.model_summaries:
        return ""
    return (
        '<section class="panel" style="margin-bottom: 18px;">'
        "<h2>Model Comparison</h2>"
        f"{render_list(forecast.model_summaries)}"
        "</section>"
    )


def render_profile_section(forecast: SailingForecast) -> str:
    if forecast.profile is None:
        return ""
    return (
        '<section class="panel profile-section" style="margin-bottom: 18px; break-inside: avoid;">'
        "<h2>ECMWF Point Sounding</h2>"
        f"{profile_chart(forecast.profile)}"
        '<div class="legend">'
        '<span><span class="swatch" style="background: #b84b42"></span>Temperature</span>'
        '<span><span class="swatch" style="background: #1e6a8d"></span>Dew point from RH</span>'
        '<span><span class="swatch" style="background: #172027"></span>Wind by pressure level</span>'
        "</div>"
        f'<p class="map-caption">ECMWF IFS pressure-level profile at {escape(forecast.profile.time_label)} near '
        f'{forecast.profile.latitude:.4f}, {forecast.profile.longitude:.4f}. This is a compact sounding-style plot, not a full thermodynamic Skew-T.</p>'
        "</section>"
    )


def profile_chart(profile: ForecastProfile) -> str:
    levels = [
        level
        for level in sorted(profile.levels, key=lambda item: item.pressure_hpa, reverse=True)
        if 300 <= level.pressure_hpa <= 1000
    ]
    if not levels:
        return empty_chart(760, 430)

    width = 760
    height = 430
    pad_left = 64
    pad_right = 118
    pad_top = 26
    pad_bottom = 44
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    min_pressure = 300
    max_pressure = 1000
    min_temp = -50
    max_temp = 35
    skew = 48

    def y_at(pressure: int | float) -> float:
        pressure = max(min_pressure, min(max_pressure, float(pressure)))
        log_min = math.log(min_pressure)
        log_max = math.log(max_pressure)
        return pad_top + ((math.log(pressure) - log_min) / (log_max - log_min)) * plot_h

    def x_at(temperature: float, pressure: int | float) -> float:
        base = pad_left + ((temperature - min_temp) / (max_temp - min_temp)) * plot_w
        return base + ((max_pressure - float(pressure)) / (max_pressure - min_pressure)) * skew

    elements: list[str] = [
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />',
        f'<rect x="{pad_left}" y="{pad_top}" width="{plot_w}" height="{plot_h}" fill="#fbfcfd" stroke="#d8e0e5" />',
    ]

    for pressure in (1000, 925, 850, 700, 600, 500, 400, 300):
        y = y_at(pressure)
        elements.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="#e7ecef" />')
        elements.append(f'<text x="{pad_left - 10}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="#5a6670">{pressure}</text>')

    for temperature in range(-50, 41, 10):
        x_bottom = x_at(temperature, max_pressure)
        x_top = x_at(temperature, min_pressure)
        elements.append(f'<line x1="{x_bottom:.1f}" y1="{y_at(max_pressure):.1f}" x2="{x_top:.1f}" y2="{y_at(min_pressure):.1f}" stroke="#edf1f3" />')
        elements.append(f'<text x="{x_bottom:.1f}" y="{height - 18}" text-anchor="middle" font-size="10" fill="#5a6670">{temperature}</text>')

    temperature_points = [
        (x_at(level.temperature_c, level.pressure_hpa), y_at(level.pressure_hpa))
        for level in levels
        if level.temperature_c is not None
    ]
    dewpoint_points = [
        (x_at(dew_point_c(level.temperature_c, level.relative_humidity_pct), level.pressure_hpa), y_at(level.pressure_hpa))
        for level in levels
        if level.temperature_c is not None and level.relative_humidity_pct is not None
    ]
    if temperature_points:
        elements.append(profile_polyline(temperature_points, "#b84b42", 3))
        for x, y in temperature_points:
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#b84b42" />')
    if dewpoint_points:
        elements.append(profile_polyline(dewpoint_points, "#1e6a8d", 3))
        for x, y in dewpoint_points:
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#1e6a8d" />')

    wind_x = width - pad_right + 54
    elements.append(f'<line x1="{wind_x:.1f}" y1="{pad_top}" x2="{wind_x:.1f}" y2="{height - pad_bottom}" stroke="#d8e0e5" />')
    for level in levels:
        if level.wind_speed_kt is None or level.wind_direction_deg is None:
            continue
        y = y_at(level.pressure_hpa)
        elements.append(render_profile_wind_barb(wind_x, y, level.wind_direction_deg, level.wind_speed_kt))

    elements.extend(
        [
            f'<text x="{pad_left}" y="16" font-size="12" fill="#5a6670">Pressure hPa</text>',
            f'<text x="{pad_left + plot_w / 2:.1f}" y="{height - 5}" text-anchor="middle" font-size="12" fill="#5a6670">Temperature deg C, skewed by pressure</text>',
            f'<text x="{wind_x:.1f}" y="16" text-anchor="middle" font-size="12" fill="#5a6670">Wind</text>',
        ]
    )

    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="ECMWF point sounding profile">{"".join(elements)}</svg>'


def profile_polyline(points: list[tuple[float, float]], color: str, width: int) -> str:
    point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" />'


def dew_point_c(temperature_c: float, relative_humidity_pct: float) -> float:
    humidity = max(1.0, min(100.0, relative_humidity_pct))
    gamma = math.log(humidity / 100.0) + (17.625 * temperature_c) / (243.04 + temperature_c)
    return (243.04 * gamma) / (17.625 - gamma)


def render_profile_wind_barb(x: float, y: float, direction: float, speed: float) -> str:
    staff_length = 25
    radians = math.radians(direction)
    ux = math.sin(radians)
    uy = -math.cos(radians)
    x2 = x + ux * staff_length
    y2 = y + uy * staff_length
    barb_angle = radians + math.radians(120)
    bx = math.sin(barb_angle)
    by = -math.cos(barb_angle)
    full_barbs = int(max(0, speed) // 10)
    half_barb = 1 if max(0, speed) % 10 >= 5 else 0
    marks = []
    offset = 2.0
    for _ in range(min(full_barbs, 5)):
        sx = x2 - ux * offset
        sy = y2 - uy * offset
        ex = sx + bx * 9
        ey = sy + by * 9
        marks.append(f'M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}')
        offset += 4.4
    if half_barb and len(marks) < 6:
        sx = x2 - ux * offset
        sy = y2 - uy * offset
        ex = sx + bx * 5
        ey = sy + by * 5
        marks.append(f'M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}')
    mark_path = " ".join(marks)
    return f'<path d="M{x:.1f},{y:.1f} L{x2:.1f},{y2:.1f} {mark_path}" stroke="#172027" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" />'


def render_synoptic_chart_section(forecast: SailingForecast) -> str:
    url = (forecast.event.synoptic_chart_url or "").strip()
    if not url:
        return ""
    safe_url = escape(url, quote=True)
    image_url = synoptic_image_url(url)
    if image_url:
        safe_image_url = escape(image_url, quote=True)
        source_link = "" if image_url == url else f'<p class="map-caption">Source page: <a class="synoptic-source" href="{safe_url}">{escape(url)}</a></p>'
        content = f'<img class="synoptic-image" src="{safe_image_url}" alt="Synoptic surface pressure chart" referrerpolicy="no-referrer">{source_link}'
    else:
        content = (
            f'<p><a class="synoptic-source" href="{safe_url}">{escape(url)}</a></p>'
            "<p class=\"map-caption\">Source page for the latest synoptic surface pressure charts. "
            "Use a direct image URL here if an embedded chart is required in the printed report.</p>"
        )
    return (
        '<section class="panel" style="margin-bottom: 18px;">'
        "<h2>Synoptic Chart</h2>"
        f"{content}"
        "</section>"
    )


def is_image_url(url: str) -> bool:
    lower = url.lower().split("?", 1)[0]
    return lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))


def synoptic_image_url(url: str) -> str | None:
    if is_image_url(url):
        return url
    return weathercharts_ukmo_image_url(url)


def weathercharts_ukmo_image_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.casefold() not in {"www.weathercharts.org", "weathercharts.org"}:
        return None
    if not parsed.path.lower().endswith("/ukmomslp.htm") and parsed.path.lower() != "/ukmomslp.htm":
        return None
    fragment = (parsed.fragment or "t0").casefold()
    chart_by_fragment = {
        "t0": "ppva.gif",
        "analysis": "ppva.gif",
        "t24": "ppve.gif",
        "t36": "ppvg.gif",
        "t48": "ppvi.gif",
        "t60": "ppvk.gif",
        "t72": "ppvm.gif",
        "t84": "ppvo.gif",
        "t96": "ppvq.gif",
        "t120": "ppvu.gif",
    }
    chart = chart_by_fragment.get(fragment, "ppva.gif")
    return f"https://www.weathercharts.net/ukmo_mslp_analysis/{chart}"


def render_navigation_tile_map(forecast: SailingForecast) -> str:
    race_area = forecast.race_area
    center_lat = race_area.latitude if race_area else forecast.venue.latitude
    center_lon = race_area.longitude if race_area else forecast.venue.longitude
    zoom = 13
    tile_size = 256
    center_x, center_y = lat_lon_to_tile(center_lat, center_lon, zoom)
    base_x = math.floor(center_x) - 1
    base_y = math.floor(center_y) - 1
    marker_left = ((center_x - base_x) / 3) * 100
    marker_top = ((center_y - base_y) / 3) * 100
    radius_px = 0
    if race_area:
        meters_per_pixel = 156543.03392 * math.cos(math.radians(center_lat)) / (2 ** zoom)
        radius_px = (race_area.radius_nm * 1852) / meters_per_pixel
    radius_percent = (radius_px / (tile_size * 3)) * 100

    images: list[str] = []
    for y_index in range(3):
        for x_index in range(3):
            x = base_x + x_index
            y = base_y + y_index
            left = x_index * 33.3334
            top = y_index * 33.3334
            osm_url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            seamark_url = f"https://tiles.openseamap.org/seamark/{zoom}/{x}/{y}.png"
            images.append(
                f'<img src="{osm_url}" alt="" style="left:{left:.4f}%; top:{top:.4f}%;">'
            )
            images.append(
                f'<img src="{seamark_url}" alt="" style="left:{left:.4f}%; top:{top:.4f}%;">'
            )

    radius = ""
    if race_area:
        radius = (
            f'<div class="race-radius" style="left:{marker_left:.3f}%; top:{marker_top:.3f}%; '
            f'width:{radius_percent * 2:.3f}%; height:{radius_percent * 2:.3f}%;"></div>'
        )
    return (
        '<div class="tile-map">'
        + "".join(images)
        + radius
        + f'<div class="venue-dot" style="left:{marker_left:.3f}%; top:{marker_top:.3f}%;"></div>'
        + "</div>"
        + f'<p class="map-caption">OpenStreetMap base with OpenSeaMap seamarks. Center: {center_lat:.4f}, {center_lon:.4f}; zoom {zoom}. Red dot marks the selected venue/race area.</p>'
    )


def lat_lon_to_tile(latitude: float, longitude: float, zoom: int) -> tuple[float, float]:
    lat_rad = math.radians(max(-85.0511, min(85.0511, latitude)))
    n = 2 ** zoom
    x = (longitude + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def render_forecast_area_maps(forecast: SailingForecast) -> str:
    area_maps = forecast.area_maps
    if not area_maps and forecast.area_points:
        area_maps = [AreaForecastMap(hour=13, time_label=forecast.area_map_time or "13:00 local", points=forecast.area_points)]
    if not area_maps:
        return "<p>No area grid data available for this report.</p>"
    maps = []
    for area_map in area_maps:
        maps.append(
            '<div class="wind-map">'
            f"<h3>{escape(area_map.time_label)} Wind Map</h3>"
            f"{render_weather_area_map(forecast, area_map, width=520, height=520)}"
            "</div>"
        )
    return f'<div class="wind-map-grid">{"".join(maps)}</div>'


def render_weather_area_map(
    forecast: SailingForecast,
    area_map: AreaForecastMap | None = None,
    width: int = 720,
    height: int = 300,
) -> str:
    points = area_map.points if area_map else forecast.area_points
    if not points:
        return "<p>No area grid data available for this map.</p>"
    zoom = 13
    tile_size = 256
    center_lat = forecast.race_area.latitude if forecast.race_area else forecast.venue.latitude
    center_lon = forecast.race_area.longitude if forecast.race_area else forecast.venue.longitude
    center_x, center_y = lat_lon_to_tile(center_lat, center_lon, zoom)
    base_x = math.floor(center_x) - 1
    base_y = math.floor(center_y) - 1
    speeds = [point.wind_speed_10m for point in points]
    min_speed, max_speed = min(speeds), max(speeds)
    time_label = area_map.time_label if area_map else forecast.area_map_time or "mid-race"

    def position(latitude: float, longitude: float) -> tuple[float, float]:
        tile_x, tile_y = lat_lon_to_tile(latitude, longitude, zoom)
        return ((tile_x - base_x) / 3) * width, ((tile_y - base_y) / 3) * height

    elements = [
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" fill="none" stroke="#172027" stroke-width="2" />',
        '<rect x="8" y="8" width="126" height="36" rx="4" fill="#ffffff" fill-opacity="0.86" stroke="#d8e0e5" />',
        '<text x="18" y="24" font-size="11" fill="#5a6670">N</text>',
        '<path d="M26,36 L26,14 M26,14 L20,24 M26,14 L32,24" stroke="#172027" stroke-width="2" fill="none" stroke-linecap="round" />',
        f'<text x="44" y="24" font-size="10" fill="#5a6670">{escape(time_label)}</text>',
        f'<text x="44" y="37" font-size="10" fill="#5a6670">{weather_map_mode_label(forecast.area_map_mode)} | 10 m wind</text>',
    ]

    label_stride = map_label_stride(len(points))

    if forecast.area_map_mode == "streamlines":
        elements.extend(render_streamlines(points, position, width, height))
        dot_radius = 3.2
        for index, point in enumerate(points):
            x, y = position(point.latitude, point.longitude)
            color = wind_speed_colour(point.wind_speed_10m, min_speed, max_speed)
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_radius}" fill="{color}" stroke="#ffffff" stroke-width="1" />')
            if index % label_stride == 0:
                elements.append(
                    f'<text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="middle" font-size="8" fill="#172027">{round(point.wind_speed_10m)}</text>'
                )
    else:
        for index, point in enumerate(points):
            x, y = position(point.latitude, point.longitude)
            color = wind_speed_colour(point.wind_speed_10m, min_speed, max_speed)
            elements.append(render_wind_barb(x, y, point, color))
            if index % label_stride == 0:
                elements.append(
                    f'<text x="{x:.1f}" y="{y + 20:.1f}" text-anchor="middle" font-size="8" fill="#172027">{round(point.wind_speed_10m)}</text>'
                )

    if forecast.race_area:
        cx, cy = position(forecast.race_area.latitude, forecast.race_area.longitude)
        meters_per_pixel = 156543.03392 * math.cos(math.radians(center_lat)) / (2 ** zoom)
        radius_px = (forecast.race_area.radius_nm * 1852) / meters_per_pixel
        radius = (radius_px / (tile_size * 3)) * width
        elements.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="#1e6a8d" fill-opacity="0.12" stroke="#1e6a8d" stroke-width="2" />')
        elements.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="#b84b42" stroke="#ffffff" stroke-width="2" />')
        elements.append(f'<text x="{cx:.1f}" y="{cy - 14:.1f}" text-anchor="middle" font-size="11" fill="#172027">{escape(forecast.race_area.name)}</text>')

    elements.append(
        f'<rect x="8" y="{height - 28}" width="132" height="18" rx="4" fill="#ffffff" fill-opacity="0.86" stroke="#d8e0e5" />'
    )
    elements.append(
        f'<text x="16" y="{height - 15}" font-size="10" fill="#5a6670">TWS {min_speed:.0f}-{max_speed:.0f} kt</text>'
    )
    images = []
    for y_index in range(3):
        for x_index in range(3):
            x = base_x + x_index
            y = base_y + y_index
            left = x_index * 33.3334
            top = y_index * 33.3334
            osm_url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            seamark_url = f"https://tiles.openseamap.org/seamark/{zoom}/{x}/{y}.png"
            images.append(f'<img src="{osm_url}" alt="" style="left:{left:.4f}%; top:{top:.4f}%;">')
            images.append(f'<img src="{seamark_url}" alt="" style="left:{left:.4f}%; top:{top:.4f}%;">')
    return (
        '<div class="tile-map forecast-tile-map">'
        + "".join(images)
        + f'<svg class="wind-overlay" viewBox="0 0 {width} {height}" role="img" aria-label="Forecast area weather map">{"".join(elements)}</svg>'
        + "</div>"
    )


def weather_map_mode_label(mode: str) -> str:
    if mode == "streamlines":
        return "Streamlines"
    return "Wind barbs"


def map_label_stride(point_count: int) -> int:
    if point_count <= 81:
        return 2
    if point_count <= 225:
        return 3
    return 4


def render_wind_barb(x: float, y: float, point: AreaForecastPoint, color: str) -> str:
    staff_length = 19
    radians = math.radians(point.wind_direction_10m)
    ux = math.sin(radians)
    uy = -math.cos(radians)
    x2 = x + ux * staff_length
    y2 = y + uy * staff_length
    barb_angle = radians + math.radians(120)
    bx = math.sin(barb_angle)
    by = -math.cos(barb_angle)
    speed = max(0, point.wind_speed_10m)
    full_barbs = int(speed // 10)
    half_barb = 1 if speed % 10 >= 5 else 0
    marks = []
    spacing = 4.3
    offset = 1.5
    for _ in range(min(full_barbs, 4)):
        sx = x2 - ux * offset
        sy = y2 - uy * offset
        ex = sx + bx * 9
        ey = sy + by * 9
        marks.append(f'M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}')
        offset += spacing
    if half_barb and len(marks) < 5:
        sx = x2 - ux * offset
        sy = y2 - uy * offset
        ex = sx + bx * 5
        ey = sy + by * 5
        marks.append(f'M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}')
    mark_path = " ".join(marks)
    return (
        f'<path d="M{x:.1f},{y:.1f} L{x2:.1f},{y2:.1f} {mark_path}" stroke="#172027" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.88" />'
        f'<path d="M{x:.1f},{y:.1f} L{x2:.1f},{y2:.1f} {mark_path}" stroke="{color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" />'
    )


def render_streamlines(
    points: list[AreaForecastPoint],
    position,
    width: int,
    height: int,
) -> list[str]:
    point_positions = [(point, *position(point.latitude, point.longitude)) for point in points]
    columns = sorted({round(point.longitude, 5) for point in points})
    rows = sorted({round(point.latitude, 5) for point in points})
    seed_points: list[tuple[float, float]] = []
    for row_index, lat_key in enumerate(rows):
        if row_index % 2 == 0:
            row_points = [item for item in point_positions if round(item[0].latitude, 5) == lat_key]
            for col_index, (_, x, y) in enumerate(sorted(row_points, key=lambda item: item[1])):
                if col_index % 2 == 0:
                    seed_points.append((x, y))
    if not seed_points:
        seed_points = [position(point.latitude, point.longitude) for point in points[:8]]

    def nearest_point(px: float, py: float) -> AreaForecastPoint:
        return min(point_positions, key=lambda item: (item[1] - px) ** 2 + (item[2] - py) ** 2)[0]

    speeds = [point.wind_speed_10m for point in points]
    min_speed, max_speed = min(speeds), max(speeds)
    elements: list[str] = []
    for seed_x, seed_y in seed_points[:25]:
        coords = [(seed_x, seed_y)]
        px = seed_x
        py = seed_y
        last_point = nearest_point(px, py)
        for _ in range(9):
            point = nearest_point(px, py)
            last_point = point
            flow_direction = (point.wind_direction_10m + 180) % 360
            radians = math.radians(flow_direction)
            step = 10 + min(8, point.wind_speed_10m * 0.45)
            px += math.sin(radians) * step
            py -= math.cos(radians) * step
            if px < 0 or px > width or py < 0 or py > height:
                break
            coords.append((px, py))
        if len(coords) < 2:
            continue
        path_data = " ".join(f"L{x:.1f},{y:.1f}" for x, y in coords[1:])
        start_x, start_y = coords[0]
        end_x, end_y = coords[-1]
        prev_x, prev_y = coords[-2]
        arrow = streamline_arrow(prev_x, prev_y, end_x, end_y)
        color = wind_speed_colour(last_point.wind_speed_10m, min_speed, max_speed)
        elements.append(
            f'<path d="M{start_x:.1f},{start_y:.1f} {path_data}" stroke="#172027" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.16" />'
        )
        elements.append(
            f'<path d="M{start_x:.1f},{start_y:.1f} {path_data}" stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" />'
        )
        elements.append(
            f'<path d="{arrow}" stroke="{color}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" />'
        )
    return elements


def streamline_arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 6
    left = angle + math.radians(150)
    right = angle - math.radians(150)
    lx = x2 + math.cos(left) * size
    ly = y2 + math.sin(left) * size
    rx = x2 + math.cos(right) * size
    ry = y2 + math.sin(right) * size
    return f'M{x2:.1f},{y2:.1f} L{lx:.1f},{ly:.1f} M{x2:.1f},{y2:.1f} L{rx:.1f},{ry:.1f}'


def wind_speed_colour(speed: float, min_speed: float, max_speed: float) -> str:
    if speed >= 30:
        return "rgb(112,48,160)"
    if speed >= 25:
        return "rgb(192,0,0)"
    if speed >= 20:
        return "rgb(255,0,0)"
    if speed >= 15:
        return "rgb(255,192,0)"
    if speed >= 10:
        return "rgb(255,255,0)"
    if speed >= 5:
        return "rgb(0,176,80)"
    if speed >= 0.1:
        return "rgb(0,112,192)"
    return "#5a6670"


def wind_speed_text_colour(speed: float) -> str:
    if speed >= 10 and speed < 20:
        return "#172027"
    return "#ffffff"


def line_chart(forecast: SailingForecast, kind: str) -> str:
    width = 520
    height = 250
    pad_left = 44
    pad_right = 18
    pad_top = 18
    pad_bottom = 34
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    labels = [hour.time_label for hour in forecast.hours]
    series = chart_series(forecast, kind)
    values = [value for item in series for value in item["values"] if value is not None]
    if kind == "speed":
        values.extend(hour.gust for hour in forecast.hours)
        values.extend(hour.lull for hour in forecast.hours)
    if not values:
        return empty_chart(width, height)

    low = min(values)
    high = max(values)
    if kind in {"speed", "cloud", "marine"}:
        low = 0
    if kind == "cloud":
        high = max(100, high)
    if low == high:
        low -= 1
        high += 1
    padding = (high - low) * 0.12
    low -= padding
    high += padding

    def x_at(index: int) -> float:
        if len(labels) == 1:
            return pad_left + plot_w / 2
        return pad_left + plot_w * index / (len(labels) - 1)

    def y_at(value: float) -> float:
        return pad_top + plot_h - ((value - low) / (high - low)) * plot_h

    grid = []
    for step in range(5):
        y = pad_top + plot_h * step / 4
        value = high - (high - low) * step / 4
        grid.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" stroke="#e7ecef" />')
        grid.append(f'<text x="8" y="{y + 4:.1f}" font-size="11" fill="#5a6670">{value:.0f}</text>')

    x_labels = []
    for index, label in enumerate(labels):
        x = x_at(index)
        short_label = chart_time_label(label)
        x_labels.append(f'<text x="{x:.1f}" y="{height - 10}" text-anchor="middle" font-size="10" fill="#5a6670">{escape(short_label)}</text>')

    fills = []
    if kind == "speed":
        fills.append(speed_envelope(forecast, x_at, y_at))

    lines = []
    for item in series:
        points = [
            f"{x_at(index):.1f},{y_at(value):.1f}"
            for index, value in enumerate(item["values"])
            if value is not None
        ]
        if points:
            lines.append(
                f'<polyline points="{" ".join(points)}" fill="none" stroke="{item["color"]}" '
                f'stroke-width="{item.get("width", 3)}" stroke-linecap="round" stroke-linejoin="round" opacity="{item.get("opacity", 1)}" />'
            )

    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{escape(kind)} chart">'
        + "".join(grid)
        + f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" stroke="#9aa6ad" />'
        + f'<line x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" stroke="#9aa6ad" />'
        + "".join(fills)
        + "".join(lines)
        + "".join(x_labels)
        + "</svg>"
    )


def chart_series(forecast: SailingForecast, kind: str) -> list[dict[str, object]]:
    model_runs = chart_model_runs(forecast)
    if kind in {"speed", "direction"}:
        return [
            {
                "name": run.name,
                "color": model_chart_color(run.name),
                "values": model_values(run.hours, forecast.hours, kind),
                "width": 3 if index == 0 else 2,
                "opacity": 1 if index == 0 else 0.72,
            }
            for index, run in enumerate(model_runs)
        ]
    if kind == "cloud":
        max_bl = max((source.boundary_layer_height or 0) for source in forecast.source_hours) or 1
        return [
            {"color": "#1e6a8d", "values": [source.cloud_cover for source in forecast.source_hours]},
            {"color": "#1d7b72", "values": [((source.boundary_layer_height or 0) / max_bl) * 100 for source in forecast.source_hours]},
        ]
    if kind == "marine":
        return [
            {"color": "#1e6a8d", "values": [source.wave_height for source in forecast.source_hours]},
        ]
    raise ValueError(f"Unknown chart kind: {kind}")


def chart_model_runs(forecast: SailingForecast) -> list[ModelForecastRun]:
    if forecast.model_runs:
        return forecast.model_runs
    return [ModelForecastRun(name=forecast.model_name, hours=forecast.source_hours)]


def model_values(model_hours: list[ForecastHour], forecast_hours: list, kind: str) -> list[float | None]:
    by_label = {}
    for hour in model_hours:
        by_label[hour.time.strftime("%H%M")] = hour
        by_label[hour.time.strftime("%m-%d %H%M")] = hour
    values: list[float | None] = []
    for forecast_hour in forecast_hours:
        source = by_label.get(forecast_hour.time_label)
        if source is None:
            values.append(None)
        elif kind == "speed":
            values.append(source.wind_speed_10m)
        else:
            values.append(source.wind_direction_10m)
    return values


def chart_time_label(label: str) -> str:
    if " " in label:
        date_part, time_part = label.split(" ", 1)
        return f"{date_part[-2:]} {time_part[:2]}"
    return label[:2]


def speed_envelope(forecast: SailingForecast, x_at, y_at) -> str:
    if not forecast.hours:
        return ""
    upper = [(x_at(index), y_at(hour.gust)) for index, hour in enumerate(forecast.hours)]
    lower = [(x_at(index), y_at(hour.lull)) for index, hour in enumerate(forecast.hours)]
    points = upper + list(reversed(lower))
    point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{point_text}" fill="#1e6a8d" opacity="0.14" />'


def chart_legend(forecast: SailingForecast, kind: str) -> str:
    if kind not in {"speed", "direction"}:
        return ""
    items = []
    if kind == "speed":
        items.append('<span><span class="swatch" style="background: rgba(30, 106, 141, 0.28)"></span>Gust-lull range</span>')
    for run in chart_model_runs(forecast):
        items.append(
            f'<span><span class="swatch" style="background: {model_chart_color(run.name)}"></span>{escape(run.name)}</span>'
        )
    return f'<div class="legend">{"".join(items)}</div>'


def model_chart_color(model_name: str) -> str:
    normalized = model_name.casefold().replace("-", "_").replace(" ", "_")
    if "ecmwf" in normalized:
        return "#1e6a8d"
    if "gfs" in normalized:
        return "#b84b42"
    if "icon" in normalized:
        return "#1b5e20"
    if "ukmo" in normalized:
        return "#b000b5"
    if "arome" in normalized and ("hd" in normalized or "france_hd" in normalized):
        return "#000000"
    if "arome" in normalized:
        return "#4a4f55"
    if "arpege" in normalized:
        return "#8a8f94"
    if "meteofrance_seamless" in normalized:
        return "#8a8f94"
    return "#5a6670"


def empty_chart(width: int, height: int) -> str:
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="No chart data">'
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />'
        f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" fill="#5a6670">No data available</text>'
        "</svg>"
    )
