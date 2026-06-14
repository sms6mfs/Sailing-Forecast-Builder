from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from sailing_forecast.app import build_custom_forecast_result, venue_payload
from sailing_forecast.model_catalog import AUTO_PRIMARY_MODEL
from sailing_forecast.model_catalog import model_payload
from sailing_forecast.models import EventMetadata
from sailing_forecast.observations import Observation, append_observation, summarize_bias


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"
OBSERVATION_PATH = ROOT / "data" / "observations.csv"


class ForecastRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def end_headers(self) -> None:
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/venues":
            self.send_json({"venues": venue_payload()})
            return
        if parsed.path == "/api/models":
            self.send_json(model_payload())
            return
        if parsed.path == "/api/bias":
            query = parse_qs(parsed.query)
            venue = query.get("venue", [None])[0]
            self.send_json(summarize_bias(OBSERVATION_PATH, venue_key=venue))
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/forecast":
            self.handle_forecast()
            return
        if parsed.path == "/api/observations":
            self.handle_observation()
            return
        self.send_error(404, "Unknown endpoint")

    def handle_forecast(self) -> None:
        try:
            payload = self.read_json()
            event = EventMetadata(
                name=payload.get("event") or "Training forecast",
                team=payload.get("team") or None,
                forecaster=payload.get("forecaster") or "Sailing Forecast Builder",
                issue_time=payload.get("issue_time") or None,
                synoptic_chart_url=payload.get("synoptic_chart_url") or None,
            )
            venue = payload["venue"]
            result = build_custom_forecast_result(
                name=venue["name"],
                latitude=float(venue["latitude"]),
                longitude=float(venue["longitude"]),
                forecast_date=payload["date"],
                start_hour=int(payload["start_hour"]),
                end_hour=int(payload["end_hour"]),
                race_area_name=venue.get("race_area_name") or "Race area",
                race_radius_nm=float(venue.get("race_radius_nm") or 2.0),
                event=event,
                model=payload.get("model") or AUTO_PRIMARY_MODEL,
                compare_models=payload.get("compare_models") or [],
                area_map_mode=payload.get("area_map_mode") or "barbs",
                area_grid_size=int(payload.get("area_grid_size") or 15),
                forecast_days=int(payload.get("forecast_days") or 1),
            )
        except Exception as error:
            self.send_json({"error": str(error)}, status=500)
            return
        self.send_json(result)

    def handle_observation(self) -> None:
        payload = self.read_json()
        observation = Observation(
            venue_key=payload["venue_key"],
            race_area=payload.get("race_area") or "",
            time_local=payload["time_local"],
            twd=int(payload["twd"]),
            tws=float(payload["tws"]),
            gust=float(payload.get("gust") or 0),
            notes=payload.get("notes") or "",
        )
        append_observation(OBSERVATION_PATH, observation)
        self.send_json({"ok": True, "bias": summarize_bias(OBSERVATION_PATH, venue_key=observation.venue_key)})

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")

    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ForecastRequestHandler)
    print(f"Sailing Forecast UI running at http://{host}:{port}")
    server.serve_forever()
