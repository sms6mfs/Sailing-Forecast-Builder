from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from sailing_forecast.app import DEFAULT_AREA_GRID_SIZE, DEFAULT_FORECAST_DAYS, build_custom_forecast_html, build_custom_forecast_text, build_forecast_html, build_forecast_text
from sailing_forecast.model_catalog import AUTO_PRIMARY_MODEL
from sailing_forecast.models import EventMetadata
from sailing_forecast.report_check import verify_html_report
from sailing_forecast.venues import VENUES
from sailing_forecast.web_server import run as run_web_server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a sailing weather forecast.")
    parser.add_argument(
        "--venue",
        choices=sorted(VENUES) if VENUES else None,
        help="Saved venue profile to forecast. Use --latitude/--longitude for a custom venue.",
    )
    parser.add_argument("--venue-name", default="Custom venue", help="Name for a custom coordinate venue.")
    parser.add_argument("--latitude", type=float, help="Custom venue latitude.")
    parser.add_argument("--longitude", type=float, help="Custom venue longitude.")
    parser.add_argument("--race-radius-nm", type=float, default=2.0, help="Custom race-area radius in nautical miles.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Forecast date in YYYY-MM-DD format.",
    )
    parser.add_argument("--start-hour", type=int, default=10, help="Local start hour.")
    parser.add_argument("--end-hour", type=int, default=18, help="Local end hour.")
    parser.add_argument("--event", default="Training forecast", help="Event name for report headers.")
    parser.add_argument("--team", help="Team or client name for report headers.")
    parser.add_argument("--forecaster", default="Sailing Forecast Builder", help="Forecaster/source label.")
    parser.add_argument("--issue-time", help="Issue time text, for example '0800 local'.")
    parser.add_argument(
        "--synoptic-chart-url",
        default="https://www.weathercharts.org/ukmomslp.htm#t0",
        help="Synoptic chart source URL to include in the report.",
    )
    parser.add_argument("--race-area", default="Race area", help="Race area name.")
    parser.add_argument(
        "--model",
        default=AUTO_PRIMARY_MODEL,
        help="Primary Open-Meteo model. Default auto-selects the highest-resolution available model; pass a model ID such as gfs_seamless to override.",
    )
    parser.add_argument(
        "--area-map-mode",
        choices=("barbs", "streamlines"),
        default="barbs",
        help="Forecast area weather map display mode.",
    )
    parser.add_argument(
        "--area-grid-size",
        type=int,
        choices=(9, 15, 21),
        default=DEFAULT_AREA_GRID_SIZE,
        help="Forecast area sampling grid size. Higher values are slower but show more local structure.",
    )
    parser.add_argument(
        "--forecast-days",
        type=int,
        choices=(1, 2),
        default=DEFAULT_FORECAST_DAYS,
        help="Number of forecast days to include in the point forecast report.",
    )
    parser.add_argument(
        "--compare-models",
        help="Comma-separated Open-Meteo models to summarize, for example gfs_seamless,ecmwf_ifs025,ukmo_seamless.",
    )
    parser.add_argument(
        "--output-html",
        help="Write a printable HTML report to this path instead of printing text.",
    )
    parser.add_argument(
        "--output-pdf",
        help="Write a PDF report to this path. Requires Playwright and a Chromium browser install.",
    )
    parser.add_argument(
        "--verify-html",
        help="Verify an existing generated HTML report and exit.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the local web UI.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve.")
    parser.add_argument("--port", type=int, default=8000, help="Port for --serve.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.serve or should_start_web_server(sys.argv[1:]):
        run_web_server(host=args.host, port=args.port)
        return

    if args.verify_html:
        result = verify_html_report(Path(args.verify_html))
        print(f"Report check: {result.path}")
        print("\n".join(result.messages))
        if not result.passed:
            raise SystemExit(1)
        return

    event = EventMetadata(
        name=args.event,
        team=args.team,
        forecaster=args.forecaster,
        issue_time=args.issue_time,
        synoptic_chart_url=args.synoptic_chart_url,
    )
    compare_models = split_csv(args.compare_models)
    if args.output_html or args.output_pdf:
        if args.latitude is not None and args.longitude is not None:
            html = build_custom_forecast_html(
                name=args.venue_name,
                latitude=args.latitude,
                longitude=args.longitude,
                forecast_date=args.date,
                start_hour=args.start_hour,
                end_hour=args.end_hour,
                race_area_name=args.race_area,
                race_radius_nm=args.race_radius_nm,
                event=event,
                model=args.model,
                compare_models=compare_models,
                area_map_mode=args.area_map_mode,
                area_grid_size=args.area_grid_size,
                forecast_days=args.forecast_days,
            )
        else:
            if not args.venue:
                raise SystemExit("Provide --latitude and --longitude, or configure a saved --venue.")
            html = build_forecast_html(
                venue_key=args.venue,
                forecast_date=args.date,
                start_hour=args.start_hour,
                end_hour=args.end_hour,
                event=event,
                race_area_name=args.race_area,
                model=args.model,
                compare_models=compare_models,
                area_map_mode=args.area_map_mode,
                area_grid_size=args.area_grid_size,
                forecast_days=args.forecast_days,
            )
        if args.output_html:
            output_path = Path(args.output_html)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            print(f"Wrote {output_path}")
        if args.output_pdf:
            output_path = Path(args.output_pdf)
            write_pdf_report(html, output_path)
            print(f"Wrote {output_path}")
        return

    if args.latitude is not None and args.longitude is not None:
        text = build_custom_forecast_text(
            name=args.venue_name,
            latitude=args.latitude,
            longitude=args.longitude,
            forecast_date=args.date,
            start_hour=args.start_hour,
            end_hour=args.end_hour,
            race_area_name=args.race_area,
            race_radius_nm=args.race_radius_nm,
            event=event,
            model=args.model,
                compare_models=compare_models,
                area_map_mode=args.area_map_mode,
                area_grid_size=args.area_grid_size,
                forecast_days=args.forecast_days,
            )
    else:
        if not args.venue:
            raise SystemExit("Provide --latitude and --longitude, or configure a saved --venue.")
        text = build_forecast_text(
            venue_key=args.venue,
            forecast_date=args.date,
            start_hour=args.start_hour,
            end_hour=args.end_hour,
            event=event,
            race_area_name=args.race_area,
            model=args.model,
            compare_models=compare_models,
            area_map_mode=args.area_map_mode,
            area_grid_size=args.area_grid_size,
            forecast_days=args.forecast_days,
        )
    print(text)


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def write_pdf_report(html: str, output_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "PDF export requires Playwright. Install it with `pip install playwright` "
            "and then run `python -m playwright install chromium`."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=str(output_path),
                format="A4",
                print_background=True,
                margin={
                    "top": "10mm",
                    "right": "10mm",
                    "bottom": "10mm",
                    "left": "10mm",
                },
            )
        finally:
            browser.close()


def should_start_web_server(argv: list[str]) -> bool:
    if not argv:
        return True
    cli_forecast_flags = ("--venue", "--latitude", "--longitude", "--output-html", "--output-pdf", "--verify-html", "--area-grid-size", "--forecast-days")
    return not any(
        arg == flag or arg.startswith(f"{flag}=")
        for arg in argv
        for flag in cli_forecast_flags
    )


if __name__ == "__main__":
    main()
