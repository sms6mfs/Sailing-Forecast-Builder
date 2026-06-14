from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportCheckResult:
    path: Path
    passed: bool
    messages: list[str]


def verify_html_report(path: Path) -> ReportCheckResult:
    html = path.read_text(encoding="utf-8")
    checks = [
        ("doctype", "<!doctype html>" in html.casefold()),
        ("print css", "@media print" in html),
        ("print color preservation", "print-color-adjust: exact" in html and "speed-cell" in html),
        ("print page groups", html.count('class="print-page') >= 2 and "print-break-before" in html),
        ("forecast title", "<h1>" in html),
        ("executive brief", "Executive Brief" in html),
        ("hourly wind table", "Hourly Sailing Wind" in html and "<table>" in html),
        ("meteorology panel", "Meteorology" in html),
        ("venue effects panel", "Venue Effects" in html),
        ("925 hPa table", "925 hPa Wind" in html and "925 hPa TWD" in html and "925 hPa TWS" in html),
        ("svg plots", html.count("<svg ") >= 8),
        ("forecast area wind maps", "Forecast Area Wind Maps" in html and html.count("aria-label=\"Forecast area weather map\"") >= 4),
        ("timed wind maps", "11:00 local Wind Map" in html and "13:00 local Wind Map" in html and "15:00 local Wind Map" in html and "17:00 local Wind Map" in html),
        ("table rows", html.count("<tr>") >= 4),
    ]
    messages = [f"{'OK' if passed else 'FAIL'}: {name}" for name, passed in checks]
    return ReportCheckResult(
        path=path,
        passed=all(passed for _, passed in checks),
        messages=messages,
    )
