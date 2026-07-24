# Sailing Forecast Builder

This project is the start of a professional sailing weather forecast generator.
The first slice fetches Open-Meteo forecast data, converts it into race-window
sailing terms, and renders a text briefing with wind ranges, gust/lull behavior,
meteorological reasoning, local effects, confidence, and sea state.

## Run

Static GitHub Pages build on the `html-only-github-pages` branch:

```powershell
cd web
python -m http.server 8008
```

Then open:

```text
http://127.0.0.1:8008
```

This branch can be published from the `web/` folder by configuring GitHub Pages
to deploy from the branch root folder that contains `index.html`, or by copying
the `web/` contents to a Pages publishing root. The static build fetches
Open-Meteo directly from the browser, so no Python server is required. Python-only
terrain, OSM cache, local file output, PDF export, and report verification remain
features of the full local/server build.

Live Open-Meteo forecast:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18
```

Printable HTML report:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --output-html reports/solent_2026-06-12.html
```

Printable HTML and PDF report:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --output-html reports/solent_2026-06-12.html --output-pdf reports/solent_2026-06-12.pdf
```

PDF export uses Playwright. Install it with `pip install playwright` and then run
`python -m playwright install chromium`.

Event, race area, and model comparison:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --event "Training Day" --team VAYU --issue-time "0800 local" --race-area "Race area" --race-radius-nm 2.5 --compare-models gfs_seamless,ecmwf_ifs025,ukmo_seamless --output-html reports/solent_models.html
```

Forecast-area map view options:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --area-map-mode barbs --output-html reports/solent_barbs.html
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --area-map-mode streamlines --output-html reports/solent_streamlines.html
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --area-grid-size 21 --output-html reports/solent_dense_grid.html
```

Multi-day point forecast:

```powershell
python main.py --venue-name "Solent Test" --latitude 50.8 --longitude -1.1 --date 2026-06-12 --start-hour 10 --end-hour 18 --forecast-days 5 --output-html reports/solent_5day.html
```

Verify a generated report:

```powershell
python main.py --verify-html reports/solent_models.html
```

Start the local web UI:

```powershell
python main.py
```

`python main.py --serve` also works, and `--host` / `--port` can be used to change the server address.

Then open:

```text
http://127.0.0.1:8000
```

Available command options:

```powershell
python main.py --help
```

## Current Capability

- Custom venue selection by latitude/longitude from the CLI.
- Custom venue selection by clicking or dragging a marker on the Leaflet map.
- Live Open-Meteo data only; no offline/sample forecast mode.
- Event metadata in text and HTML reports.
- Configurable race-area name and radius.
- Provisional local-effects notes for custom venues until shoreline/topography rules are configured.
- Open-Meteo weather and marine API calls.
- Primary Open-Meteo model selection.
- Multi-model summary when requested and available from Open-Meteo.
- Expanded Open-Meteo model catalog covering the documented forecast model list.
- Windy Point Forecast model metadata for future API-key integration.
- Surface wind, gusts, 925 hPa gradient, cloud, boundary layer, CAPE, temperature,
  waves, SST, and current ingestion where available.
- Derived sea-breeze diagnostics using air-SST contrast, cloud trend, solar
  radiation, pressure tendency, race-area pressure spread, and boundary-layer
  mixing.
- Hourly TWD/TWS ranges with gust and lull estimates.
- First-pass detection of thermal bends, cloud-modulated flow, patchy light air,
  gradient-dominant days, and confidence.
- Text forecast output suitable for reviewing the analysis logic.
- Printable HTML report with briefing panels, an hourly table, and inline SVG plots.
- Static HTML report verification for print CSS, core sections, tables, and plots.
- Local web UI with a Leaflet venue map, OpenSeaMap seamarks enabled by default,
  map-click venue selection, race-area circles, primary model selection,
  1- to 5-day forecast selection, multi-model comparison selection,
  navigation-map wind overlays, report preview, and print-to-PDF workflow.
- Observation capture to `data/observations.csv` for future model-bias tracking.
- Open-Meteo 9x9 area-grid sampling around the selected race area.
- EU-DEM terrain scan for European venues via Open Topo Data `eudem25m`, with
  cached elevation lookups and advisory terrain notes in local effects.
- OpenStreetMap wooded and built-up landuse scan via Overpass API, with cached
  5 nm / 10 nm ring and compass-sector surface roughness notes.
- Generated 11:00, 13:00, 15:00 and 17:00 forecast-area wind maps with selectable
  10 m wind barbs or streamlines, gust coloring, cloud shading, and pressure labels.
- Configurable forecast-area sampling grids: 9x9, 15x15, or 21x21 points. Higher
  settings are slower but show more local structure from the source model grid.
- Forecast API returns the same local wind maps as JSON objects so the web UI can
  plot the selected time directly on the Leaflet navigation map. Area wind maps
  remain scoped to the selected start date, while tables, charts, and outlook
  sections use the full selected forecast length.
- 925 hPa wind table for 11:00, 13:00, 15:00 and 17:00 local time.
- If the selected high-resolution primary model does not provide 925 hPa winds,
  the report fills those pressure-level winds from ECMWF IFS 0.25 while keeping
  the selected model as the primary surface forecast.
- ECMWF IFS point-sounding chart at the bottom of the HTML/PDF report, using
  pressure-level temperature, relative humidity-derived dew point, and wind barbs.

## Terrain Data

European terrain notes use the Open Topo Data public API endpoint
`https://api.opentopodata.org/v1/eudem25m`. The scan queries a 21x21 DEM box grid
with a 10 nm half-width around the forecast point. Results are cached in
`data/elevation_cache.json` to avoid repeated calls. The public API is best used
for lightweight enrichment only: requests are batched, `null` elevations near
coasts and offshore race areas are tolerated, and the generated notes should be
treated as advisory local-effect prompts rather than deterministic wind
corrections.

Wooded and built-up surface notes use OpenStreetMap feature tags queried through
Overpass API. The classifier looks for wooded tags such as `natural=wood` and
`landuse=forest`, plus built-up landuse tags such as `residential`,
`commercial`, `industrial`, `retail`, and `construction`. Results are cached in
`data/osm_geography_cache.json`. Individual building footprints are deliberately
not queried because they can produce very large results in towns and cities.

## Next Build Step

The next step should be improving the data quality and report polish:

- Store forecast snapshots alongside observations, then calculate model bias by
  venue, race area, model, wind sector, and time of day.
- Add real browser PDF export checks when a browser automation dependency is available.
- Add more venue profiles and tune sector rules from real forecast/observation examples.
- Add editable custom venues and race areas from the UI.
- Add a Windy API key setting and Windy Point Forecast adapter so Windy-supported
  models can be used as real forecast sources, not just catalog metadata.
- Add higher-resolution and time-stepped area maps, with controls for map time,
  grid size, and map variable.

## Model Catalog

Selectable Open-Meteo model IDs currently exposed in the UI:

- `auto_highest_resolution` (default; resolves to the highest-resolution available explicit model)
- `best_match`
- `ecmwf_ifs`
- `ecmwf_ifs025`
- `ecmwf_aifs025_single`
- `cma_grapes_global`
- `bom_access_global`
- `gfs_seamless`
- `gfs_global`
- `gfs_hrrr`
- `ncep_nbm_conus`
- `ncep_nam_conus`
- `gfs_graphcast025`
- `ncep_aigfs025`
- `ncep_hgefs025_ensemble_mean`
- `jma_seamless`
- `jma_msm`
- `jma_gsm`
- `kma_seamless`
- `kma_ldps`
- `kma_gdps`
- `icon_seamless`
- `icon_global`
- `icon_eu`
- `icon_d2`
- `gem_seamless`
- `gem_global`
- `gem_regional`
- `gem_hrdps_continental`
- `gem_hrdps_west`
- `meteofrance_seamless`
- `meteofrance_arpege_world`
- `meteofrance_arpege_europe`
- `meteofrance_arome_france`
- `meteofrance_arome_france_hd`
- `italia_meteo_arpae_icon_2i`
- `metno_seamless`
- `metno_nordic`
- `knmi_seamless`
- `knmi_harmonie_arome_europe`
- `knmi_harmonie_arome_netherlands`
- `dmi_seamless`
- `dmi_harmonie_arome_europe`
- `ukmo_seamless`
- `ukmo_global_deterministic_10km`
- `ukmo_uk_deterministic_2km`
- `meteoswiss_icon_seamless`
- `meteoswiss_icon_ch1`
- `meteoswiss_icon_ch2`
- `geosphere_seamless`
- `geosphere_arome_austria`
