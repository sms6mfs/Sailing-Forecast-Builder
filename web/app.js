const WEATHER_HOURLY = [
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
];

const MARINE_HOURLY = [
  "wave_height",
  "wave_direction",
  "wave_period",
  "sea_surface_temperature",
  "ocean_current_velocity",
  "ocean_current_direction",
];

const AUTO_PRIMARY_MODEL = "auto_highest_resolution";
const AREA_MAP_HOURS = [11, 13, 15, 17];

const HIGHEST_RESOLUTION_MODEL_ORDER = [
  "meteoswiss_icon_ch1",
  "meteoswiss_icon_ch2",
  "metno_nordic",
  "icon_d2",
  "knmi_harmonie_arome_netherlands",
  "knmi_harmonie_arome_europe",
  "dmi_harmonie_arome_europe",
  "geosphere_arome_austria",
  "italia_meteo_arpae_icon_2i",
  "meteofrance_arome_france_hd",
  "meteofrance_arome_france",
  "ukmo_uk_deterministic_2km",
  "gem_hrdps_continental",
  "gem_hrdps_west",
  "gfs_hrrr",
  "ncep_nbm_conus",
  "ncep_nam_conus",
  "jma_msm",
  "kma_ldps",
  "meteofrance_arpege_europe",
  "icon_eu",
  "ukmo_global_deterministic_10km",
  "ecmwf_ifs",
  "gem_regional",
  "kma_gdps",
  "meteofrance_arpege_world",
  "cma_grapes_global",
  "bom_access_global",
  "gem_global",
  "ecmwf_ifs025",
  "ecmwf_aifs025_single",
  "gfs_global",
  "gfs_graphcast025",
  "ncep_aigfs025",
  "ncep_hgefs025_ensemble_mean",
  "icon_global",
  "jma_gsm",
  "gfs_seamless",
];

const OPEN_METEO_MODELS = [
  ["Open-Meteo", AUTO_PRIMARY_MODEL, "Highest resolution available", "Automatic"],
  ["Open-Meteo", "best_match", "Best match", "Automatic"],
  ["ECMWF", "ecmwf_ifs", "ECMWF IFS HRES 9 km", "Global"],
  ["ECMWF", "ecmwf_ifs025", "ECMWF IFS 0.25 deg", "Global"],
  ["ECMWF", "ecmwf_aifs025_single", "ECMWF AIFS 0.25 deg single", "Global"],
  ["CMA", "cma_grapes_global", "CMA GRAPES global", "Global"],
  ["BOM", "bom_access_global", "BOM ACCESS global", "Global"],
  ["NCEP", "gfs_seamless", "NCEP GFS seamless", "Global"],
  ["NCEP", "gfs_global", "NCEP GFS global 0.11/0.25 deg", "Global"],
  ["NCEP", "gfs_hrrr", "NCEP HRRR U.S. CONUS", "United States"],
  ["NCEP", "ncep_nbm_conus", "NCEP NBM U.S. CONUS", "United States"],
  ["NCEP", "ncep_nam_conus", "NCEP NAM U.S. CONUS", "United States"],
  ["NCEP", "gfs_graphcast025", "NCEP GFS GraphCast", "Global"],
  ["NCEP", "ncep_aigfs025", "NCEP AIGFS 0.25 deg", "Global"],
  ["NCEP", "ncep_hgefs025_ensemble_mean", "NCEP HGEFS 0.25 deg ensemble mean", "Global"],
  ["JMA", "jma_seamless", "JMA seamless", "Automatic / Japan-global"],
  ["JMA", "jma_msm", "JMA MSM", "Japan region"],
  ["JMA", "jma_gsm", "JMA GSM", "Global"],
  ["KMA", "kma_seamless", "KMA seamless", "Automatic / Korea-global"],
  ["KMA", "kma_ldps", "KMA LDPS", "Korea region"],
  ["KMA", "kma_gdps", "KMA GDPS", "Global"],
  ["DWD", "icon_seamless", "DWD ICON seamless", "Automatic / Europe-global"],
  ["DWD", "icon_global", "DWD ICON global", "Global"],
  ["DWD", "icon_eu", "DWD ICON EU", "Europe"],
  ["DWD", "icon_d2", "DWD ICON D2", "Central Europe"],
  ["GEM", "gem_seamless", "GEM seamless", "Automatic / Canada-global"],
  ["GEM", "gem_global", "GEM global", "Global"],
  ["GEM", "gem_regional", "GEM regional", "North America"],
  ["GEM", "gem_hrdps_continental", "GEM HRDPS continental", "Canada region"],
  ["GEM", "gem_hrdps_west", "GEM HRDPS west", "Western Canada"],
  ["Meteo-France", "meteofrance_seamless", "Meteo-France seamless", "Automatic / Europe"],
  ["Meteo-France", "meteofrance_arpege_world", "Meteo-France ARPEGE world", "Global"],
  ["Meteo-France", "meteofrance_arpege_europe", "Meteo-France ARPEGE Europe", "Europe"],
  ["Meteo-France", "meteofrance_arome_france", "Meteo-France AROME France", "France region"],
  ["Meteo-France", "meteofrance_arome_france_hd", "Meteo-France AROME France HD", "France region"],
  ["ItaliaMeteo", "italia_meteo_arpae_icon_2i", "ItaliaMeteo ARPAE ICON 2I", "Italy region"],
  ["MET Norway", "metno_seamless", "MET Norway Nordic seamless", "Nordic region"],
  ["MET Norway", "metno_nordic", "MET Norway Nordic", "Nordic region"],
  ["KNMI", "knmi_seamless", "KNMI seamless", "Netherlands / Europe"],
  ["KNMI", "knmi_harmonie_arome_europe", "KNMI Harmonie AROME Europe", "Europe"],
  ["KNMI", "knmi_harmonie_arome_netherlands", "KNMI Harmonie AROME Netherlands", "Netherlands"],
  ["DMI", "dmi_seamless", "DMI seamless", "Denmark / Europe"],
  ["DMI", "dmi_harmonie_arome_europe", "DMI Harmonie AROME Europe", "Europe"],
  ["UK Met Office", "ukmo_seamless", "UK Met Office seamless", "Automatic / UK-global"],
  ["UK Met Office", "ukmo_global_deterministic_10km", "UK Met Office global 10 km", "Global"],
  ["UK Met Office", "ukmo_uk_deterministic_2km", "UK Met Office UK 2 km", "UK region"],
  ["MeteoSwiss", "meteoswiss_icon_seamless", "MeteoSwiss ICON seamless", "Switzerland region"],
  ["MeteoSwiss", "meteoswiss_icon_ch1", "MeteoSwiss ICON CH1", "Switzerland region"],
  ["MeteoSwiss", "meteoswiss_icon_ch2", "MeteoSwiss ICON CH2", "Switzerland region"],
  ["GeoSphere", "geosphere_seamless", "GeoSphere seamless", "Austria region"],
  ["GeoSphere", "geosphere_arome_austria", "GeoSphere AROME Austria", "Austria region"],
].map(([provider, model_id, label, region]) => ({ provider, model_id, label, region, selectable: true }));

const DEFAULT_COMPARE_MODELS = ["gfs_seamless", "ecmwf_ifs025", "meteofrance_seamless", "ukmo_seamless"];

const state = {
  selectedVenue: null,
  selectedRaceArea: null,
  venueMarker: null,
  areaLayers: [],
  windLayer: null,
  windMaps: [],
  reportHtml: "",
  models: OPEN_METEO_MODELS,
  defaultCompareModels: DEFAULT_COMPARE_MODELS,
};

const map = L.map("map", { zoomControl: true }).setView([20, 0], 2);
const osmLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);
const openSeaMapLayer = L.tileLayer("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "Map data &copy; OpenSeaMap contributors",
}).addTo(map);
L.control.layers({ "OpenStreetMap": osmLayer }, { "OpenSeaMap seamarks": openSeaMapLayer }, { collapsed: false }).addTo(map);

const venueName = document.querySelector("#venue-name");
const venueLatitude = document.querySelector("#venue-latitude");
const venueLongitude = document.querySelector("#venue-longitude");
const raceAreaName = document.querySelector("#race-area-name");
const raceRadius = document.querySelector("#race-radius");
const modelSelect = document.querySelector("#model-select");
const compareModels = document.querySelector("#compare-models");
const modelNote = document.querySelector("#model-note");
const statusEl = document.querySelector("#status");
const reportFrame = document.querySelector("#report-frame");
const printButton = document.querySelector("#print-report");
const windMapTime = document.querySelector("#wind-map-time");
const mapModeSelect = document.querySelector("select[name='area_map_mode']");

document.querySelector("#forecast-form").addEventListener("submit", generateForecast);
venueLatitude.addEventListener("change", updateVenueFromInputs);
venueLongitude.addEventListener("change", updateVenueFromInputs);
venueName.addEventListener("change", updateVenueFromInputs);
raceAreaName.addEventListener("change", updateVenueFromInputs);
raceRadius.addEventListener("change", updateVenueFromInputs);
windMapTime.addEventListener("change", renderWindMapOverlay);
mapModeSelect.addEventListener("change", renderWindMapOverlay);
map.on("click", (event) => setVenuePoint(event.latlng.lat, event.latlng.lng));
printButton.addEventListener("click", async () => {
  if (reportFrame.contentWindow) {
    statusEl.textContent = "Preparing report images for print...";
    await waitForReportImages();
    reportFrame.contentWindow.focus();
    reportFrame.contentWindow.print();
    statusEl.textContent = "Print dialog opened.";
  }
});

init();

function init() {
  setDefaultDate();
  renderModelControls();
  statusEl.textContent = "Click the map or enter coordinates to set a custom venue.";
}

function setDefaultDate() {
  document.querySelector("input[name='date']").value = new Date().toISOString().slice(0, 10);
}

function renderModelControls() {
  modelSelect.innerHTML = groupedModels(state.models)
    .map(([provider, models]) => (
      `<optgroup label="${escapeHtml(provider)}">` +
      models.map((model) => `<option value="${model.model_id}">${escapeHtml(model.label)} - ${escapeHtml(model.region)}</option>`).join("") +
      `</optgroup>`
    ))
    .join("");
  modelSelect.value = AUTO_PRIMARY_MODEL;
  compareModels.innerHTML = state.models
    .map((model) => (
      `<label title="${escapeHtml(model.region)}"><input type="checkbox" value="${model.model_id}" ${state.defaultCompareModels.includes(model.model_id) ? "checked" : ""}>${escapeHtml(model.provider)} - ${escapeHtml(model.label)}</label>`
    ))
    .join("");
  modelNote.textContent = `${state.models.length} Open-Meteo models available. This static build runs fully in the browser.`;
}

function groupedModels(models) {
  const groups = [];
  models.forEach((model) => {
    const provider = model.provider || "Open-Meteo";
    let group = groups.find(([name]) => name === provider);
    if (!group) {
      group = [provider, []];
      groups.push(group);
    }
    group[1].push(model);
  });
  return groups;
}

function setVenuePoint(latitude, longitude, name = venueName.value || "Custom venue") {
  venueName.value = name;
  venueLatitude.value = Number(latitude).toFixed(4);
  venueLongitude.value = Number(longitude).toFixed(4);
  updateVenueFromInputs();
  map.setView([latitude, longitude], Math.max(map.getZoom(), 10));
}

function updateVenueFromInputs() {
  const latitude = Number(venueLatitude.value);
  const longitude = Number(venueLongitude.value);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    statusEl.textContent = "Click the map or enter valid latitude and longitude.";
    return;
  }
  const radiusNm = Number(raceRadius.value || 2);
  const key = slugify(venueName.value) || `custom_${latitude.toFixed(4)}_${longitude.toFixed(4)}`;
  state.selectedVenue = { key, name: venueName.value || "Custom venue", latitude, longitude, timezone: "auto" };
  state.selectedRaceArea = { name: raceAreaName.value || "Race area", latitude, longitude, radius_nm: radiusNm };
  clearWindMapOverlay();
  renderVenuePoint();
  renderRaceAreas();
  statusEl.textContent = `Venue set at ${latitude.toFixed(4)}, ${longitude.toFixed(4)}.`;
}

function clearWindMapOverlay() {
  if (state.windLayer) {
    state.windLayer.remove();
    state.windLayer = null;
  }
  state.windMaps = [];
  windMapTime.disabled = true;
  windMapTime.innerHTML = "<option>No forecast</option>";
}

function renderVenuePoint() {
  if (!state.selectedVenue) {
    return;
  }
  const latlng = [state.selectedVenue.latitude, state.selectedVenue.longitude];
  if (!state.venueMarker) {
    state.venueMarker = L.marker(latlng, { draggable: true }).addTo(map);
    state.venueMarker.on("dragend", () => {
      const point = state.venueMarker.getLatLng();
      setVenuePoint(point.lat, point.lng);
    });
  } else {
    state.venueMarker.setLatLng(latlng);
  }
  state.venueMarker.bindPopup(`<strong>${escapeHtml(state.selectedVenue.name)}</strong><br>Drag marker or click map to move venue.`);
}

function renderRaceAreas() {
  state.areaLayers.forEach((layer) => layer.remove());
  state.areaLayers = [];
  if (!state.selectedRaceArea) {
    return;
  }
  const area = state.selectedRaceArea;
  const circle = L.circle([area.latitude, area.longitude], {
    radius: area.radius_nm * 1852,
    color: "#1e6a8d",
    weight: 3,
    fillColor: "#1e6a8d",
    fillOpacity: 0.18,
  }).addTo(map);
  circle.bindPopup(`<strong>${escapeHtml(area.name)}</strong><br>${area.radius_nm} nm race area`);
  state.areaLayers.push(circle);
}

async function generateForecast(event) {
  event.preventDefault();
  if (!state.selectedVenue || !state.selectedRaceArea) {
    statusEl.textContent = "Click the map to set a venue first.";
    return;
  }
  statusEl.textContent = "Fetching Open-Meteo data...";
  printButton.disabled = true;
  const form = new FormData(event.currentTarget);
  const payload = {
    event: form.get("event") || "Training forecast",
    team: form.get("team") || "",
    issue_time: form.get("issue_time") || "",
    synoptic_chart_url: form.get("synoptic_chart_url") || "",
    venue: {
      name: form.get("venue_name") || "Custom venue",
      latitude: Number(form.get("latitude")),
      longitude: Number(form.get("longitude")),
      timezone: "auto",
    },
    race_area: {
      name: form.get("race_area_name") || "Race area",
      latitude: Number(form.get("latitude")),
      longitude: Number(form.get("longitude")),
      radius_nm: Number(form.get("race_radius_nm") || 2),
    },
    date: form.get("date"),
    start_hour: Number(form.get("start_hour")),
    end_hour: Number(form.get("end_hour")),
    forecast_days: normalizeForecastDays(form.get("forecast_days")),
    model: form.get("model") || AUTO_PRIMARY_MODEL,
    area_map_mode: form.get("area_map_mode") || "barbs",
    area_grid_size: normalizeAreaGridSize(form.get("area_grid_size")),
    compare_models: selectedCompareModels(),
  };
  try {
    const result = await buildForecastResult(payload);
    state.reportHtml = result.html;
    reportFrame.onload = () => {
      statusEl.textContent = "Report generated. Map images are loading; use Print Report after preview is visible.";
    };
    reportFrame.srcdoc = result.html;
    state.windMaps = result.wind_maps || [];
    renderWindMapTimeOptions();
    renderWindMapOverlay();
    printButton.disabled = false;
    statusEl.textContent = "Report generated. Loading preview...";
  } catch (error) {
    statusEl.textContent = `Forecast failed: ${error.message}`;
  }
}

async function buildForecastResult(payload) {
  const [resolvedModel, hours] = await fetchPrimaryForecast(payload.venue, payload.date, payload.model, payload.forecast_days);
  statusEl.textContent = `Primary model ${resolvedModel} loaded. Fetching comparison models...`;
  const raceHours = hours.filter((hour) => payload.start_hour <= hour.time.getHours() && hour.time.getHours() <= payload.end_hour);
  if (!raceHours.length) {
    throw new Error("No forecast data found for the requested race window.");
  }
  const comparisonModels = payload.compare_models.filter((item) => ![payload.model, resolvedModel, AUTO_PRIMARY_MODEL].includes(item));
  const comparisonRuns = await fetchModelRuns(payload.venue, payload.date, comparisonModels, payload.start_hour, payload.end_hour, payload.forecast_days);
  const modelRuns = [{ name: resolvedModel, hours: raceHours }, ...comparisonRuns.runs];
  statusEl.textContent = "Fetching race-area wind maps...";
  const areaMaps = await fetchAreaMaps(payload.race_area, payload.date, AREA_MAP_HOURS, resolvedModel, payload.area_grid_size);
  const forecast = analyzeForecast(payload, resolvedModel, raceHours, modelRuns, comparisonRuns.unavailable, areaMaps);
  return {
    html: renderForecastHtml(forecast),
    wind_maps: areaMaps.map((areaMap) => ({
      hour: areaMap.hour,
      time_label: areaMap.time_label,
      points: areaMap.points,
    })),
  };
}

async function fetchPrimaryForecast(venue, forecastDate, requestedModel, forecastDays) {
  if (requestedModel !== AUTO_PRIMARY_MODEL) {
    return [requestedModel, await fetchForecast(venue, forecastDate, requestedModel, forecastDays)];
  }
  const failures = [];
  for (const model of HIGHEST_RESOLUTION_MODEL_ORDER) {
    try {
      const hours = await fetchForecast(venue, forecastDate, model, forecastDays);
      if (hours.length) {
        return [model, hours];
      }
      failures.push(`${model}: no hourly data`);
    } catch (error) {
      failures.push(`${model}: ${error.message}`);
    }
  }
  throw new Error(`No explicit Open-Meteo model was available. ${failures.slice(0, 4).join("; ")}`);
}

async function fetchForecast(venue, forecastDate, model, forecastDays) {
  const weatherParams = {
    latitude: venue.latitude,
    longitude: venue.longitude,
    timezone: venue.timezone || "auto",
    start_date: forecastDate,
    end_date: forecastEndDate(forecastDate, forecastDays),
    wind_speed_unit: "kn",
    hourly: WEATHER_HOURLY.join(","),
  };
  if (model) {
    weatherParams.models = model;
  }
  const weather = await openMeteoJson("https://api.open-meteo.com/v1/forecast", weatherParams);
  let marine = null;
  try {
    marine = await openMeteoJson("https://marine-api.open-meteo.com/v1/marine", {
      latitude: venue.latitude,
      longitude: venue.longitude,
      timezone: venue.timezone || "auto",
      start_date: forecastDate,
      end_date: forecastEndDate(forecastDate, forecastDays),
      length_unit: "metric",
      cell_selection: "sea",
      hourly: MARINE_HOURLY.join(","),
    });
  } catch {
    marine = null;
  }
  return mergeHourly(weather.hourly, marine ? marine.hourly : null);
}

async function openMeteoJson(baseUrl, params) {
  const url = `${baseUrl}?${new URLSearchParams(params).toString().replaceAll("%2C", ",")}`;
  const response = await fetch(url);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.reason || body.error || response.statusText);
  }
  return body;
}

function mergeHourly(weather, marine) {
  const marineByTime = new Map();
  if (marine) {
    (marine.time || []).forEach((time, index) => marineByTime.set(time, index));
  }
  return (weather.time || []).map((timeText, index) => {
    const marineIndex = marineByTime.get(timeText);
    return {
      time: new Date(timeText),
      time_text: timeText,
      temperature_2m: valueAt(weather, "temperature_2m", index),
      sea_level_pressure: valueAt(weather, "pressure_msl", index),
      cloud_cover: valueAt(weather, "cloud_cover", index),
      cloud_cover_low: valueAt(weather, "cloud_cover_low", index),
      wind_speed_10m: valueAt(weather, "wind_speed_10m", index) || 0,
      wind_direction_10m: valueAt(weather, "wind_direction_10m", index) || 0,
      wind_gust_10m: valueAt(weather, "wind_gusts_10m", index) || 0,
      shortwave_radiation: valueAt(weather, "shortwave_radiation", index),
      cape: valueAt(weather, "cape", index),
      boundary_layer_height: valueAt(weather, "boundary_layer_height", index),
      wind_speed_925hpa: valueAt(weather, "wind_speed_925hPa", index),
      wind_direction_925hpa: valueAt(weather, "wind_direction_925hPa", index),
      sea_surface_temperature: marineValueAt(marine, marineIndex, "sea_surface_temperature"),
      wave_height: marineValueAt(marine, marineIndex, "wave_height"),
      wave_direction: marineValueAt(marine, marineIndex, "wave_direction"),
      wave_period: marineValueAt(marine, marineIndex, "wave_period"),
      ocean_current_velocity: marineValueAt(marine, marineIndex, "ocean_current_velocity"),
      ocean_current_direction: marineValueAt(marine, marineIndex, "ocean_current_direction"),
    };
  });
}

async function fetchModelRuns(venue, forecastDate, models, startHour, endHour, forecastDays) {
  const runs = [];
  const unavailable = [];
  for (const model of models) {
    try {
      const hours = (await fetchForecast(venue, forecastDate, model, forecastDays))
        .filter((hour) => startHour <= hour.time.getHours() && hour.time.getHours() <= endHour);
      if (hours.length) {
        runs.push({ name: model, hours });
      }
    } catch (error) {
      unavailable.push(`${model}: unavailable (${error.message})`);
    }
  }
  return { runs, unavailable };
}

async function fetchAreaMaps(raceArea, forecastDate, targetHours, model, gridSize) {
  const points = gridPoints(raceArea, gridSize);
  const batches = chunked(points, 180);
  const mapsByHour = new Map(targetHours.map((hour) => [hour, []]));
  for (const batch of batches) {
    const batchMaps = await fetchAreaMapsBatch(batch, forecastDate, targetHours, model);
    batchMaps.forEach((areaMap) => {
      mapsByHour.get(areaMap.hour).push(...areaMap.points);
    });
  }
  return targetHours.map((hour) => ({ hour, time_label: `${String(hour).padStart(2, "0")}:00 local`, points: mapsByHour.get(hour) || [] }));
}

async function fetchAreaMapsBatch(points, forecastDate, targetHours, model) {
  const params = {
    latitude: points.map(([latitude]) => latitude.toFixed(5)).join(","),
    longitude: points.map(([, longitude]) => longitude.toFixed(5)).join(","),
    timezone: "auto",
    start_date: forecastDate,
    end_date: forecastDate,
    wind_speed_unit: "kn",
    hourly: "wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,pressure_msl",
  };
  if (model) {
    params.models = model;
  }
  const weather = await openMeteoJson("https://api.open-meteo.com/v1/forecast", params);
  const locations = Array.isArray(weather) ? weather : [weather];
  return targetHours.map((targetHour) => {
    const mapPoints = [];
    points.forEach(([latitude, longitude], pointIndex) => {
      const location = locations[pointIndex];
      if (!location || !location.hourly) {
        return;
      }
      const hourly = location.hourly;
      const index = closestHourIndex(hourly.time || [], targetHour);
      mapPoints.push({
        latitude,
        longitude,
        wind_direction_10m: valueAt(hourly, "wind_direction_10m", index) || 0,
        wind_speed_10m: valueAt(hourly, "wind_speed_10m", index) || 0,
        wind_gust_10m: valueAt(hourly, "wind_gusts_10m", index) || 0,
        cloud_cover: valueAt(hourly, "cloud_cover", index),
        sea_level_pressure: valueAt(hourly, "pressure_msl", index),
      });
    });
    return { hour: targetHour, time_label: `${String(targetHour).padStart(2, "0")}:00 local`, points: mapPoints };
  });
}

function analyzeForecast(payload, modelName, raceHours, modelRuns, unavailableModels, areaMaps) {
  const sailingHours = raceHours.map((hour) => analyzeHour(hour));
  const [executiveHours, executiveModel] = executiveSourceHours(modelRuns, raceHours, modelName);
  const executiveSailingHours = executiveHours.map((hour) => analyzeHour(hour));
  const typeOfDay = typeOfDay(raceHours);
  return {
    event: payload.event,
    team: payload.team,
    issue_time: payload.issue_time,
    synoptic_chart_url: payload.synoptic_chart_url,
    venue: payload.venue,
    race_area: payload.race_area,
    forecast_date: payload.date,
    race_window: `${String(payload.start_hour).padStart(2, "0")}00-${String(payload.end_hour).padStart(2, "0")}00 local`,
    model_name: modelName,
    type_of_day: typeOfDay,
    confidence: confidence(raceHours),
    executive_summary: summary(typeOfDay, executiveSailingHours, executiveHours, executiveModel),
    meteorology: meteorology(raceHours, areaMaps),
    local_effects: localEffects(payload.race_area, raceHours),
    hours: sailingHours,
    source_hours: raceHours,
    area_maps: areaMaps,
    area_map_mode: payload.area_map_mode,
    model_summaries: [...summarizeModelRuns(modelRuns.slice(1), unavailableModels), "Static GitHub Pages build: Open-Meteo is fetched directly from the browser."],
    marine_summary: marineSummary(raceHours),
    model_runs: modelRuns,
  };
}

function analyzeHour(hour) {
  const meanDir = roundedDirection(hour.wind_direction_10m);
  const gustDelta = Math.max(1, hour.wind_gust_10m - hour.wind_speed_10m);
  const cloud = hour.cloud_cover || 0;
  const instability = (hour.cape || 0) > 100 ? 1 : 0;
  const spread = clamp(6 + gustDelta * 1.6 + cloud / 18 + instability * 4, 8, 28);
  const lullDelta = clamp(gustDelta * 0.55 + cloud / 35, 1, 8);
  const speedSpread = clamp(gustDelta * 0.55 + cloud / 45, 1.5, 5.5);
  return {
    time_label: hour.timeText || hour.time_text.slice(11, 13) + "00",
    twd_mean: meanDir,
    twd_min: roundedDirection(meanDir - spread, 5),
    twd_max: roundedDirection(meanDir + spread, 5),
    tws_mean: Math.round(hour.wind_speed_10m),
    tws_min: Math.max(0, Math.round(hour.wind_speed_10m - speedSpread)),
    tws_max: Math.round(hour.wind_speed_10m + speedSpread),
    gust: Math.round(hour.wind_gust_10m),
    lull: Math.max(0, Math.round(hour.wind_speed_10m - lullDelta)),
    phase: phase(hour, gustDelta, spread),
    note: hourNote(hour, gustDelta),
  };
}

function phase(hour, gustDelta, spread) {
  if (hour.wind_speed_10m < 6) {
    return "patchy";
  }
  if (spread > 20) {
    return "shifty";
  }
  if (gustDelta >= 5) {
    return "gust-led";
  }
  if (hour.wind_direction_925hpa != null && angularDifference(hour.wind_direction_10m, hour.wind_direction_925hpa) > 35) {
    return "thermal bend";
  }
  return "steady";
}

function hourNote(hour, gustDelta) {
  const notes = [];
  if (hour.wind_direction_925hpa != null && angularDifference(hour.wind_direction_10m, hour.wind_direction_925hpa) > 35) {
    notes.push("surface breeze is bent away from gradient");
  }
  if ((hour.cloud_cover || 0) > 60) {
    notes.push("cloud may soften pressure");
  }
  if (gustDelta >= 5) {
    notes.push("noticeable gust-lull spread");
  }
  if (hour.wind_speed_10m < 6) {
    notes.push("look for pressure patches");
  }
  return notes.length ? notes.join("; ") : "normal phase range";
}

function executiveSourceHours(modelRuns, fallbackHours, primaryModelName) {
  if (!modelRuns.length) {
    return [fallbackHours, null];
  }
  const primary = modelRuns.find((run) => run.name === primaryModelName && run.hours.length);
  if (primary) {
    return [primary.hours, primary.name];
  }
  const preferredOrder = [
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
  ];
  for (const modelName of preferredOrder) {
    const run = modelRuns.find((item) => item.name === modelName && item.hours.length);
    if (run) {
      return [run.hours, run.name];
    }
  }
  const first = modelRuns.find((run) => run.hours.length);
  return first ? [first.hours, first.name] : [fallbackHours, null];
}

function typeOfDay(hours) {
  const avgSpeed = mean(hours.map((hour) => hour.wind_speed_10m));
  const avgCloud = mean(hours.map((hour) => hour.cloud_cover || 0));
  const avgRadiation = mean(hours.map((hour) => hour.shortwave_radiation || 0));
  const thermalTurn = angularDifference(hours[0].wind_direction_10m, hours[hours.length - 1].wind_direction_10m);
  const gradientGap = mean(hours.filter((hour) => hour.wind_direction_925hpa != null).map((hour) => angularDifference(hour.wind_direction_10m, hour.wind_direction_925hpa))) || 0;
  if (avgSpeed < 6 && avgRadiation > 350) {
    return "light thermal / patchy pressure day";
  }
  if (thermalTurn > 25 && gradientGap > 25) {
    return "thermal-bend day over a separate gradient";
  }
  if (avgCloud > 65) {
    return "cloud-modulated gradient day";
  }
  if (avgSpeed >= 14 && gradientGap < 25) {
    return "gradient-dominant day";
  }
  return "mixed gradient and thermal day";
}

function confidence(hours) {
  const directionStd = pstdev(hours.map((hour) => hour.wind_direction_10m));
  const avgCloud = mean(hours.map((hour) => hour.cloud_cover || 0));
  const avgSpeed = mean(hours.map((hour) => hour.wind_speed_10m));
  let score = 8;
  if (directionStd > 25) score -= 2;
  if (avgCloud > 60) score -= 1;
  if (avgSpeed < 6) score -= 2;
  if (angularDifference(hours[0].wind_direction_10m, hours[hours.length - 1].wind_direction_10m) > 35) score -= 1;
  const label = score >= 7 ? "high" : score >= 5 ? "moderate" : "low";
  return `${label} (${score}/10)`;
}

function summary(type, sailingHours, sourceHours, modelName) {
  const start = sailingHours[0];
  const end = sailingHours[sailingHours.length - 1];
  const avgGustDelta = mean(sourceHours.map((hour) => hour.wind_gust_10m - hour.wind_speed_10m));
  const trend = end.tws_mean > start.tws_mean + 2 ? "building" : end.tws_mean < start.tws_mean - 2 ? "easing" : "fairly level";
  const bend = directionTrend(start.twd_mean, end.twd_mean);
  const source = modelName ? ` using ${modelName}` : "";
  return `${capitalize(type)}${source}. Breeze starts around ${padDir(start.twd_mean)} at ${start.tws_mean} kt and finishes around ${padDir(end.twd_mean)} at ${end.tws_mean} kt; speed trend is ${trend}, direction trend is ${bend}. Expected gust-lull delta is about ${Math.round(avgGustDelta)} kt, with the largest tactical value in pressure differences when the breeze is under 8 kt or cloud increases.`;
}

function meteorology(hours, areaMaps) {
  const avgSurfaceDir = circularMean(hours.map((hour) => hour.wind_direction_10m));
  const avgSurfaceSpeed = mean(hours.map((hour) => hour.wind_speed_10m));
  const gradientHours = hours.filter((hour) => hour.wind_direction_925hpa != null && hour.wind_speed_925hpa != null);
  const avgCloud = mean(hours.map((hour) => hour.cloud_cover || 0));
  const avgBl = mean(hours.map((hour) => hour.boundary_layer_height || 0));
  const avgCape = mean(hours.map((hour) => hour.cape || 0));
  const bullets = [
    `Surface flow averages ${padDir(roundedDirection(avgSurfaceDir))} at ${Math.round(avgSurfaceSpeed)} kt through the race window.`,
    `Cloud cover averages ${Math.round(avgCloud)}%, so cloud impact is ${avgCloud > 55 ? "material" : "limited"}.`,
    `Boundary layer height averages about ${Math.round(avgBl)} m; mixing potential is ${avgBl > 700 ? "good" : "shallow to moderate"}.`,
    ...thermalAndPressureDiagnostics(hours, areaMaps),
  ];
  if (gradientHours.length) {
    const avgGradDir = circularMean(gradientHours.map((hour) => hour.wind_direction_925hpa || 0));
    const avgGradSpeed = mean(gradientHours.map((hour) => hour.wind_speed_925hpa || 0));
    const gap = angularDifference(avgSurfaceDir, avgGradDir);
    bullets.splice(1, 0, `925 hPa gradient averages ${padDir(roundedDirection(avgGradDir))} at ${Math.round(avgGradSpeed)} kt; surface-gradient separation is about ${Math.round(gap)} degrees.`);
  }
  bullets.push(avgCape > 100 ? "CAPE is high enough to increase gust and cloud-line uncertainty." : "CAPE is low, so gusts should mostly come from mixing, terrain and pressure patches rather than deep convection.");
  return bullets;
}

function thermalAndPressureDiagnostics(hours, areaMaps) {
  const bullets = [];
  const temperatureHours = hours.filter((hour) => hour.temperature_2m != null);
  const sstHours = hours.filter((hour) => hour.sea_surface_temperature != null);
  const radiationHours = hours.filter((hour) => hour.shortwave_radiation != null);
  const pressureHours = hours.filter((hour) => hour.sea_level_pressure != null);
  if (temperatureHours.length && sstHours.length) {
    const avgAir = mean(temperatureHours.map((hour) => hour.temperature_2m || 0));
    const avgSst = mean(sstHours.map((hour) => hour.sea_surface_temperature || 0));
    const contrast = avgAir - avgSst;
    const contrastNote = contrast >= 3 ? "supports a thermally driven onshore component if the gradient allows it" : contrast <= -1 ? "favours stable marine air and weaker thermal mixing" : "is modest, so thermal forcing is not dominant by itself";
    bullets.push(`Air-SST contrast averages ${contrast >= 0 ? "+" : ""}${contrast.toFixed(1)} C (${avgAir.toFixed(1)} C air vs ${avgSst.toFixed(1)} C sea); ${contrastNote}.`);
  }
  if (hours.length >= 2) {
    const cloudStart = hours[0].cloud_cover || 0;
    const cloudEnd = hours[hours.length - 1].cloud_cover || 0;
    const cloudChange = cloudEnd - cloudStart;
    const radiation = radiationHours.length ? mean(radiationHours.map((hour) => hour.shortwave_radiation || 0)) : 0;
    const trend = cloudChange > 15 ? "increasing" : cloudChange < -15 ? "clearing" : "fairly steady";
    bullets.push(`Cloud trend is ${trend} (${Math.round(cloudStart)}% to ${Math.round(cloudEnd)}%) with mean shortwave radiation around ${Math.round(radiation)} W/m2.`);
  }
  if (pressureHours.length >= 2) {
    const pressureChange = (pressureHours[pressureHours.length - 1].sea_level_pressure || 0) - (pressureHours[0].sea_level_pressure || 0);
    const tendency = pressureChange > 0.7 ? "rising" : pressureChange < -0.7 ? "falling" : "near steady";
    bullets.push(`MSLP tendency is ${tendency}, changing ${pressureChange >= 0 ? "+" : ""}${pressureChange.toFixed(1)} hPa across the race window.`);
  }
  const spread = areaPressureSpreadChange(areaMaps);
  if (spread) {
    const [startLabel, startSpread, endLabel, endSpread] = spread;
    const change = endSpread - startSpread;
    const gradientNote = change > 0.2 ? "tightening" : change < -0.2 ? "relaxing" : "little changed";
    bullets.push(`Race-area pressure spread is ${gradientNote}: ${startSpread.toFixed(1)} hPa at ${startLabel} to ${endSpread.toFixed(1)} hPa at ${endLabel}.`);
  }
  const [score, reason] = seaBreezePotential(hours);
  bullets.push(`Sea-breeze potential score is ${score}/10: ${reason}`);
  return bullets;
}

function seaBreezePotential(hours) {
  const avgSpeed = mean(hours.map((hour) => hour.wind_speed_10m));
  const avgCloud = mean(hours.map((hour) => hour.cloud_cover || 0));
  const avgBl = mean(hours.map((hour) => hour.boundary_layer_height || 0));
  const avgRadiation = mean(hours.map((hour) => hour.shortwave_radiation || 0));
  const thermalTurn = angularDifference(hours[0].wind_direction_10m, hours[hours.length - 1].wind_direction_10m);
  const temperatureHours = hours.filter((hour) => hour.temperature_2m != null && hour.sea_surface_temperature != null);
  const airSstContrast = temperatureHours.length ? mean(temperatureHours.map((hour) => (hour.temperature_2m || 0) - (hour.sea_surface_temperature || 0))) : 0;
  let score = 0;
  const reasons = [];
  if (airSstContrast >= 4) {
    score += 3;
    reasons.push("warm air over cooler sea");
  } else if (airSstContrast >= 2) {
    score += 2;
    reasons.push("some land-sea thermal contrast");
  } else if (airSstContrast >= 0.5) {
    score += 1;
    reasons.push("weak thermal contrast");
  }
  if (avgRadiation >= 550) {
    score += 3;
    reasons.push("strong solar input");
  } else if (avgRadiation >= 300) {
    score += 2;
    reasons.push("usable solar input");
  } else if (avgRadiation >= 150) {
    score += 1;
    reasons.push("limited solar input");
  }
  if (avgCloud <= 35) {
    score += 2;
    reasons.push("low cloud cover");
  } else if (avgCloud <= 60) {
    score += 1;
    reasons.push("partial cloud");
  }
  if (avgSpeed >= 4 && avgSpeed <= 12) {
    score += 1;
    reasons.push("gradient is light to moderate");
  } else if (avgSpeed > 16) {
    reasons.push("stronger gradient may suppress a separate sea breeze");
  }
  if (avgBl >= 600) {
    score += 1;
    reasons.push("boundary layer can mix");
  }
  if (thermalTurn >= 20) {
    score += 1;
    reasons.push("forecast already shows a thermal-style direction turn");
  }
  return [Math.round(clamp(score, 0, 10)), `${reasons.length ? reasons.join(", ") : "weak thermal signal in the available fields"}.`];
}

function localEffects(raceArea) {
  return [
    `Race area: ${raceArea.name}, centered near ${raceArea.latitude.toFixed(3)}, ${raceArea.longitude.toFixed(3)}, radius about ${Number(raceArea.radius_nm).toFixed(1).replace(/\.0$/, "")} nm.`,
    "Static build note: venue-specific DEM/OSM geography analysis is not included because GitHub Pages cannot write or cache local Python data.",
    "Treat local-effect notes as provisional and refine with observations, shoreline geometry and course location.",
  ];
}

function summarizeModelRuns(modelRuns, unavailable) {
  const summaries = [...(unavailable || [])];
  modelRuns.forEach((run) => {
    const avgDir = circularMean(run.hours.map((hour) => hour.wind_direction_10m));
    const avgSpeed = mean(run.hours.map((hour) => hour.wind_speed_10m));
    summaries.push(`${run.name}: averages ${padDir(roundedDirection(avgDir))} at ${Math.round(avgSpeed)} kt.`);
  });
  if (modelRuns.length >= 2) {
    const avgDirs = modelRuns.map((run) => circularMean(run.hours.map((hour) => hour.wind_direction_10m)));
    const avgSpeeds = modelRuns.map((run) => mean(run.hours.map((hour) => hour.wind_speed_10m)));
    const dirSpread = Math.max(...avgDirs.slice(1).map((direction) => angularDifference(avgDirs[0], direction)));
    const speedSpread = Math.max(...avgSpeeds) - Math.min(...avgSpeeds);
    summaries.push(`Model spread: direction spread about ${Math.round(dirSpread)} degrees; speed spread about ${speedSpread.toFixed(1)} kt.`);
  }
  return summaries;
}

function marineSummary(hours) {
  const waveHours = hours.filter((hour) => hour.wave_height != null);
  if (!waveHours.length) {
    return null;
  }
  const avgWave = mean(waveHours.map((hour) => hour.wave_height || 0));
  const periodHours = waveHours.filter((hour) => hour.wave_period != null);
  const directionHours = waveHours.filter((hour) => hour.wave_direction != null);
  const avgPeriod = periodHours.length ? mean(periodHours.map((hour) => hour.wave_period || 0)) : 0;
  const avgDir = directionHours.length ? circularMean(directionHours.map((hour) => hour.wave_direction || 0)) : 0;
  return `Sea state: mean wave height around ${avgWave.toFixed(1)} m from ${padDir(roundedDirection(avgDir))}, period about ${Math.round(avgPeriod)} s.`;
}

function renderForecastHtml(forecast) {
  const issued = forecast.source_hours[0] ? forecast.source_hours[0].time_text.slice(0, 10) : forecast.forecast_date;
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(forecast.venue.name)} Sailing Forecast</title>
  <style>${reportCss()}</style>
</head>
<body>
  <main class="page">
    <header>
      <div>
        <h1>${escapeHtml(forecast.event)}</h1>
        <p>${escapeHtml(forecast.venue.name)} - ${escapeHtml(capitalize(forecast.type_of_day))}</p>
      </div>
      <div class="meta">
        <div>Team: ${escapeHtml(forecast.team || "n/a")}</div>
        <div>Issue: ${escapeHtml(forecast.issue_time || issued)}</div>
        <div>Date: ${escapeHtml(forecast.forecast_date)}</div>
        <div>Race window: ${escapeHtml(forecast.race_window)}</div>
        <div>Race area: ${escapeHtml(forecast.race_area.name)}</div>
        <div>Primary model: ${escapeHtml(forecast.model_name)}</div>
        <div>Confidence: ${escapeHtml(forecast.confidence)}</div>
        <div>Source: Open-Meteo APIs direct from browser</div>
      </div>
    </header>
    <section class="brief">
      <div class="band">
        <h2>Executive Brief</h2>
        <p>${escapeHtml(forecast.executive_summary)}</p>
      </div>
      <div class="panel">
        <h2>Key Numbers</h2>
        ${renderKeyFacts(forecast)}
      </div>
    </section>
    ${renderSynopticChartSection(forecast)}
    <section><h2>925 hPa Wind</h2>${render925Table(forecast)}</section>
    <section><h2>Hourly Sailing Wind</h2>${renderHourTable(forecast)}</section>
    <section class="panel"><h2>Forecast Area Wind Maps</h2>${renderForecastAreaMaps(forecast)}</section>
    <section class="grid-2">
      <div class="panel"><h2>Meteorology</h2>${renderList(forecast.meteorology)}</div>
      <div class="panel"><h2>Venue Effects</h2>${renderList(forecast.local_effects)}</div>
    </section>
    ${forecast.model_summaries.length ? `<section class="panel"><h2>Model Comparison</h2>${renderList(forecast.model_summaries)}</section>` : ""}
    <footer>Generated for planning and race briefing. ${escapeHtml(forecast.marine_summary || "")}</footer>
  </main>
</body>
</html>`;
}

function reportCss() {
  return `
    :root { --ink:#172027; --muted:#5a6670; --line:#d8e0e5; --panel:#f6f8f9; --blue:#1e6a8d; --teal:#1d7b72; --red:#b84b42; }
    * { box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
    body { margin:0; color:var(--ink); background:#eef3f5; font-family:Arial, Helvetica, sans-serif; line-height:1.35; }
    .page { max-width:1120px; margin:0 auto; padding:28px; background:white; min-height:100vh; }
    header { display:grid; grid-template-columns:1fr auto; gap:18px; border-bottom:3px solid var(--ink); padding-bottom:16px; margin-bottom:18px; }
    h1,h2,h3,p { margin-top:0; } h1 { font-size:30px; margin-bottom:6px; } h2 { font-size:17px; margin-bottom:10px; }
    .meta { display:grid; gap:4px; color:var(--muted); font-size:13px; text-align:right; }
    .brief,.grid-2,.wind-map-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:18px; }
    .band,.panel { border:1px solid var(--line); border-radius:6px; padding:14px; background:var(--panel); margin-bottom:18px; }
    .band { border-left:6px solid var(--blue); background:white; }
    .facts { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; } .fact { border-left:4px solid var(--teal); padding-left:10px; }
    .fact b { display:block; font-size:20px; } .fact span { color:var(--muted); font-size:12px; }
    table { width:100%; border-collapse:collapse; font-size:13px; margin-bottom:18px; } th { text-align:left; background:var(--ink); color:white; padding:7px 8px; }
    td { border-bottom:1px solid var(--line); padding:7px 8px; vertical-align:top; } td.num { font-variant-numeric:tabular-nums; white-space:nowrap; }
    ul { padding-left:18px; margin:0; } li { margin-bottom:7px; }
    .tile-map { position:relative; width:100%; max-width:520px; aspect-ratio:1; margin:0 auto; overflow:hidden; background:#d8e0e5; border:2px solid var(--ink); border-radius:4px; }
    .tile-map img { position:absolute; width:33.3334%; height:33.3334%; object-fit:cover; }
    .wind-overlay { position:absolute; inset:0; z-index:5; width:100%; height:100%; background:transparent; pointer-events:none; }
    .map-caption, footer { color:var(--muted); font-size:12px; }
    .synoptic-image { width:100%; max-height:520px; object-fit:contain; border:1px solid var(--line); background:white; }
    .speed-cell { font-weight:700; }
    @media print { @page { size:A4; margin:8mm; } body{background:white;font-size:10px}.page{padding:0;max-width:none} table{font-size:8px}.panel,.band{padding:7px} }
    @media screen and (max-width:800px) { .page{padding:18px} header,.brief,.grid-2,.wind-map-grid{grid-template-columns:1fr}.meta{text-align:left}.facts{grid-template-columns:1fr} }
  `;
}

function renderKeyFacts(forecast) {
  const speeds = forecast.hours.map((hour) => hour.tws_mean);
  const gusts = forecast.hours.map((hour) => hour.gust);
  const directions = forecast.hours.map((hour) => hour.twd_mean);
  const shift = directions.length >= 2 ? angularDifference(directions[0], directions[directions.length - 1]) : 0;
  return `<div class="facts">
    <div class="fact"><b>${Math.min(...speeds)}-${Math.max(...speeds)} kt</b><span>Mean wind range</span></div>
    <div class="fact"><b>${Math.max(...gusts)} kt</b><span>Peak forecast gust</span></div>
    <div class="fact"><b>${Math.round(shift)} deg</b><span>Net direction change</span></div>
  </div>`;
}

function renderSynopticChartSection(forecast) {
  if (!forecast.synoptic_chart_url) {
    return "";
  }
  const url = escapeHtml(forecast.synoptic_chart_url);
  return `<section class="panel"><h2>Synoptic Chart</h2><p class="map-caption"><a href="${url}" target="_blank" rel="noreferrer">Open synoptic chart source</a></p></section>`;
}

function render925Table(forecast) {
  const targetHours = [11, 13, 15, 17];
  const header = targetHours.map((hour) => `<th>${String(hour).padStart(2, "0")}:00 local</th>`).join("");
  const directions = targetHours.map((hour) => {
    const source = closestSourceHour(forecast.source_hours, hour);
    return `<td class="num">${source && source.wind_direction_925hpa != null ? padDir(Math.round(source.wind_direction_925hpa)) : "n/a"}</td>`;
  }).join("");
  const speeds = targetHours.map((hour) => {
    const source = closestSourceHour(forecast.source_hours, hour);
    return speedCell(source ? source.wind_speed_925hpa : null);
  }).join("");
  return `<table><thead><tr><th>Time</th>${header}</tr></thead><tbody><tr><th>925 hPa TWD</th>${directions}</tr><tr><th>925 hPa TWS</th>${speeds}</tr></tbody></table>`;
}

function renderHourTable(forecast) {
  const rows = forecast.hours.map((hour) => `<tr>
    <td class="num">${escapeHtml(hour.time_label)}</td>
    <td class="num">${padDir(hour.twd_mean)}</td>
    <td class="num">${padDir(hour.twd_min)}-${padDir(hour.twd_max)}</td>
    ${speedCell(hour.tws_mean)}
    <td class="num">${hour.tws_min}-${hour.tws_max} kt</td>
    ${speedCell(hour.gust)}
    ${speedCell(hour.lull)}
    <td>${escapeHtml(hour.phase)}</td>
    <td>${escapeHtml(hour.note)}</td>
  </tr>`).join("");
  return `<table><thead><tr><th>Time</th><th>TWD</th><th>TWD range</th><th>TWS</th><th>TWS range</th><th>Gust</th><th>Lull</th><th>Phase</th><th>Notes</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderForecastAreaMaps(forecast) {
  if (!forecast.area_maps.length) {
    return "<p>No area grid data available for this report.</p>";
  }
  return `<div class="wind-map-grid">${forecast.area_maps.map((areaMap) => `<div class="wind-map"><h3>${escapeHtml(areaMap.time_label)} Wind Map</h3>${renderWeatherAreaMap(forecast, areaMap)}</div>`).join("")}</div>`;
}

function renderWeatherAreaMap(forecast, areaMap) {
  const points = areaMap.points || [];
  if (!points.length) {
    return "<p>No area grid data available for this map.</p>";
  }
  const width = 520;
  const height = 520;
  const zoom = 13;
  const centerLat = forecast.race_area.latitude;
  const centerLon = forecast.race_area.longitude;
  const [centerX, centerY] = latLonToTile(centerLat, centerLon, zoom);
  const baseX = Math.floor(centerX) - 1;
  const baseY = Math.floor(centerY) - 1;
  const speeds = points.map((point) => point.wind_speed_10m);
  const minSpeed = Math.min(...speeds);
  const maxSpeed = Math.max(...speeds);
  const position = (latitude, longitude) => {
    const [tileX, tileY] = latLonToTile(latitude, longitude, zoom);
    return [((tileX - baseX) / 3) * width, ((tileY - baseY) / 3) * height];
  };
  const elements = [
    `<rect x="1" y="1" width="${width - 2}" height="${height - 2}" fill="none" stroke="#172027" stroke-width="2"></rect>`,
    `<text x="16" y="${height - 15}" font-size="10" fill="#5a6670">TWS ${minSpeed.toFixed(0)}-${maxSpeed.toFixed(0)} kt</text>`,
  ];
  const stride = windLabelStride(points.length);
  points.forEach((point, index) => {
    const [x, y] = position(point.latitude, point.longitude);
    const color = windSpeedColor(point.wind_speed_10m);
    elements.push(renderWindBarbSvgPath(x, y, point, color));
    if (index % stride === 0) {
      elements.push(`<text x="${x.toFixed(1)}" y="${(y + 20).toFixed(1)}" text-anchor="middle" font-size="8" fill="#172027">${Math.round(point.wind_speed_10m)}</text>`);
    }
  });
  const [cx, cy] = position(forecast.race_area.latitude, forecast.race_area.longitude);
  const metersPerPixel = 156543.03392 * Math.cos(centerLat * Math.PI / 180) / (2 ** zoom);
  const radius = ((forecast.race_area.radius_nm * 1852) / metersPerPixel / (256 * 3)) * width;
  elements.push(`<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${radius.toFixed(1)}" fill="#1e6a8d" fill-opacity="0.12" stroke="#1e6a8d" stroke-width="2"></circle>`);
  elements.push(`<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="5" fill="#b84b42" stroke="#ffffff" stroke-width="2"></circle>`);
  const images = [];
  for (let yIndex = 0; yIndex < 3; yIndex += 1) {
    for (let xIndex = 0; xIndex < 3; xIndex += 1) {
      const x = baseX + xIndex;
      const y = baseY + yIndex;
      images.push(`<img src="https://tile.openstreetmap.org/${zoom}/${x}/${y}.png" alt="" style="left:${(xIndex * 33.3334).toFixed(4)}%; top:${(yIndex * 33.3334).toFixed(4)}%;">`);
      images.push(`<img src="https://tiles.openseamap.org/seamark/${zoom}/${x}/${y}.png" alt="" style="left:${(xIndex * 33.3334).toFixed(4)}%; top:${(yIndex * 33.3334).toFixed(4)}%;">`);
    }
  }
  return `<div class="tile-map">${images.join("")}<svg class="wind-overlay" viewBox="0 0 ${width} ${height}" role="img" aria-label="Forecast area weather map">${elements.join("")}</svg></div>`;
}

function renderWindBarbSvgPath(x, y, point, color) {
  const staffLength = 19;
  const radians = (Number(point.wind_direction_10m) || 0) * Math.PI / 180;
  const ux = Math.sin(radians);
  const uy = -Math.cos(radians);
  const x2 = x + ux * staffLength;
  const y2 = y + uy * staffLength;
  const barbAngle = radians + 120 * Math.PI / 180;
  const bx = Math.sin(barbAngle);
  const by = -Math.cos(barbAngle);
  const speed = Math.max(0, Number(point.wind_speed_10m) || 0);
  const fullBarbs = Math.floor(speed / 10);
  const halfBarb = speed % 10 >= 5;
  const marks = [];
  let offset = 1.5;
  for (let index = 0; index < Math.min(fullBarbs, 4); index += 1) {
    const sx = x2 - ux * offset;
    const sy = y2 - uy * offset;
    const ex = sx + bx * 9;
    const ey = sy + by * 9;
    marks.push(`M${sx.toFixed(1)},${sy.toFixed(1)} L${ex.toFixed(1)},${ey.toFixed(1)}`);
    offset += 4.3;
  }
  if (halfBarb && marks.length < 5) {
    const sx = x2 - ux * offset;
    const sy = y2 - uy * offset;
    const ex = sx + bx * 5;
    const ey = sy + by * 5;
    marks.push(`M${sx.toFixed(1)},${sy.toFixed(1)} L${ex.toFixed(1)},${ey.toFixed(1)}`);
  }
  const path = `M${x.toFixed(1)},${y.toFixed(1)} L${x2.toFixed(1)},${y2.toFixed(1)} ${marks.join(" ")}`;
  return `<path d="${path}" stroke="#172027" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.88"></path><path d="${path}" stroke="${color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>`;
}

function renderList(items) {
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function speedCell(speed) {
  if (speed == null) {
    return '<td class="num">n/a</td>';
  }
  const background = windSpeedColor(Number(speed));
  const color = Number(speed) >= 10 && Number(speed) < 20 ? "#172027" : "#ffffff";
  return `<td class="num speed-cell" style="background-color:${background}; color:${color};">${Math.round(speed)} kt</td>`;
}

function renderWindMapTimeOptions() {
  windMapTime.innerHTML = "";
  if (!state.windMaps.length) {
    windMapTime.disabled = true;
    windMapTime.innerHTML = "<option>No forecast</option>";
    return;
  }
  windMapTime.disabled = false;
  windMapTime.innerHTML = state.windMaps.map((windMap) => `<option value="${windMap.hour}">${escapeHtml(windMap.time_label)}</option>`).join("");
  const preferred = state.windMaps.find((windMap) => Number(windMap.hour) === 13) || state.windMaps[0];
  windMapTime.value = String(preferred.hour);
}

function renderWindMapOverlay() {
  if (state.windLayer) {
    state.windLayer.remove();
    state.windLayer = null;
  }
  if (!state.windMaps.length || windMapTime.disabled) {
    return;
  }
  const selectedHour = Number(windMapTime.value);
  const windMap = state.windMaps.find((item) => Number(item.hour) === selectedHour) || state.windMaps[0];
  if (!windMap || !windMap.points || !windMap.points.length) {
    return;
  }
  state.windLayer = L.layerGroup().addTo(map);
  if (mapModeSelect.value === "streamlines") {
    renderStreamlineOverlay(windMap.points, state.windLayer);
  } else {
    renderBarbOverlay(windMap.points, state.windLayer);
  }
}

function renderBarbOverlay(points, layer) {
  points.forEach((point, index) => {
    const marker = L.marker([point.latitude, point.longitude], {
      interactive: true,
      icon: L.divIcon({
        className: "selector-wind-barb",
        html: windBarbHtml(point, index, points),
        iconSize: [52, 52],
        iconAnchor: [26, 26],
      }),
    }).addTo(layer);
    marker.bindPopup(windPointPopup(point));
  });
}

function windBarbHtml(point, index, points) {
  const stride = windLabelStride(points.length);
  const label = index % stride === 0 ? `<span class="wind-speed-label">${Math.round(point.wind_speed_10m)}</span>` : "";
  return `${windBarbSvg(point)}${label}`;
}

function windLabelStride(pointCount) {
  if (pointCount <= 81) return 2;
  if (pointCount <= 225) return 3;
  return 4;
}

function windBarbSvg(point) {
  const color = windSpeedColor(point.wind_speed_10m);
  return `<svg class="selector-wind-barb-svg" viewBox="0 0 52 52" aria-hidden="true">${renderWindBarbSvgPath(26, 26, point, color)}</svg>`;
}

function renderStreamlineOverlay(points, layer) {
  const seeds = points.filter((_, index) => index % 2 === 0);
  seeds.forEach((seed) => {
    const line = buildStreamline(seed, points);
    if (line.length < 2) return;
    const color = windSpeedColor(seed.wind_speed_10m);
    L.polyline(line, { color, weight: 3, opacity: 0.85, lineCap: "round", lineJoin: "round" }).addTo(layer);
    L.circleMarker(line[line.length - 1], { radius: 3, color, fillColor: color, fillOpacity: 0.9, weight: 1 }).bindPopup(windPointPopup(seed)).addTo(layer);
  });
}

function buildStreamline(seed, points) {
  const latitudes = points.map((point) => Number(point.latitude));
  const longitudes = points.map((point) => Number(point.longitude));
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);
  const minLon = Math.min(...longitudes);
  const maxLon = Math.max(...longitudes);
  const step = Math.min(maxLat - minLat || 0.01, maxLon - minLon || 0.01) / 2.4;
  const line = [[Number(seed.latitude), Number(seed.longitude)]];
  let latitude = Number(seed.latitude);
  let longitude = Number(seed.longitude);
  for (let index = 0; index < 8; index += 1) {
    const nearest = nearestWindPoint(latitude, longitude, points);
    const direction = ((Number(nearest.wind_direction_10m) || 0) + 180) % 360;
    const radians = direction * Math.PI / 180;
    latitude += Math.cos(radians) * step;
    longitude += Math.sin(radians) * step / Math.max(0.2, Math.cos(latitude * Math.PI / 180));
    if (latitude < minLat || latitude > maxLat || longitude < minLon || longitude > maxLon) break;
    line.push([latitude, longitude]);
  }
  return line;
}

function nearestWindPoint(latitude, longitude, points) {
  return points.reduce((best, point) => {
    const bestDistance = (best.latitude - latitude) ** 2 + (best.longitude - longitude) ** 2;
    const distance = (point.latitude - latitude) ** 2 + (point.longitude - longitude) ** 2;
    return distance < bestDistance ? point : best;
  }, points[0]);
}

function windPointPopup(point) {
  const pressure = point.sea_level_pressure == null ? "n/a" : `${Math.round(point.sea_level_pressure)} hPa`;
  const cloud = point.cloud_cover == null ? "n/a" : `${Math.round(point.cloud_cover)}%`;
  return `<strong>Open-Meteo grid point</strong><br>TWD ${Math.round(point.wind_direction_10m)} | TWS ${Math.round(point.wind_speed_10m)} kt<br>Gust ${Math.round(point.wind_gust_10m)} kt | Cloud ${cloud}<br>Pressure ${pressure}`;
}

function windSpeedColor(speed) {
  const value = Number(speed) || 0;
  if (value >= 30) return "rgb(112,48,160)";
  if (value >= 25) return "rgb(192,0,0)";
  if (value >= 20) return "rgb(255,0,0)";
  if (value >= 15) return "rgb(255,192,0)";
  if (value >= 10) return "rgb(255,255,0)";
  if (value >= 5) return "rgb(0,176,80)";
  if (value >= 0.1) return "rgb(0,112,192)";
  return "#5a6670";
}

function gridPoints(raceArea, gridSize) {
  const half = Math.max(1, Math.floor(gridSize / 2));
  const latStep = (raceArea.radius_nm * 1.852) / 111 / 2;
  const lonStep = latStep / Math.max(0.2, Math.abs(Math.cos(raceArea.latitude * Math.PI / 180)));
  const points = [];
  for (let y = -half; y <= half; y += 1) {
    for (let x = -half; x <= half; x += 1) {
      points.push([raceArea.latitude + y * latStep, raceArea.longitude + x * lonStep]);
    }
  }
  return points;
}

function areaPressureSpreadChange(areaMaps) {
  const spreads = areaMaps
    .map((areaMap) => {
      const pressures = areaMap.points.map((point) => point.sea_level_pressure).filter((value) => value != null);
      return pressures.length >= 2 ? [areaMap.time_label, Math.max(...pressures) - Math.min(...pressures)] : null;
    })
    .filter(Boolean);
  if (spreads.length < 2) {
    return null;
  }
  return [spreads[0][0], spreads[0][1], spreads[spreads.length - 1][0], spreads[spreads.length - 1][1]];
}

function closestSourceHour(hours, targetHour) {
  return hours.reduce((best, hour) => {
    if (!best) return hour;
    return Math.abs(hour.time.getHours() - targetHour) < Math.abs(best.time.getHours() - targetHour) ? hour : best;
  }, null);
}

function closestHourIndex(times, targetHour) {
  let bestIndex = 0;
  let bestDelta = 24;
  times.forEach((timeText, index) => {
    const hour = new Date(timeText).getHours();
    const delta = Math.abs(hour - targetHour);
    if (delta < bestDelta) {
      bestIndex = index;
      bestDelta = delta;
    }
  });
  return bestIndex;
}

function valueAt(hourly, key, index) {
  const values = hourly ? hourly[key] : null;
  if (!values) return null;
  return values[index] == null ? null : values[index];
}

function marineValueAt(marine, index, key) {
  if (!marine || index == null) return null;
  return valueAt(marine, key, index);
}

function forecastEndDate(forecastDate, forecastDays) {
  const date = new Date(`${forecastDate}T00:00:00`);
  date.setDate(date.getDate() + Math.max(1, Math.min(5, Number(forecastDays) || 1)) - 1);
  return date.toISOString().slice(0, 10);
}

function normalizeAreaGridSize(value) {
  const gridSize = Number(value || 15);
  return [9, 15, 21].includes(gridSize) ? gridSize : 15;
}

function normalizeForecastDays(value) {
  const days = Number(value || 1);
  return [1, 2, 3, 4, 5].includes(days) ? days : 1;
}

function chunked(items, size) {
  const chunks = [];
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size));
  }
  return chunks;
}

function latLonToTile(latitude, longitude, zoom) {
  const latRad = Math.max(-85.0511, Math.min(85.0511, latitude)) * Math.PI / 180;
  const n = 2 ** zoom;
  const x = (longitude + 180) / 360 * n;
  const y = (1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2 * n;
  return [x, y];
}

function circularMean(values) {
  const valid = values.filter((value) => Number.isFinite(value));
  if (!valid.length) return 0;
  const sin = mean(valid.map((value) => Math.sin(value * Math.PI / 180)));
  const cos = mean(valid.map((value) => Math.cos(value * Math.PI / 180)));
  return (Math.atan2(sin, cos) * 180 / Math.PI + 360) % 360;
}

function angularDifference(a, b) {
  return Math.abs(((a - b + 540) % 360) - 180);
}

function roundedDirection(value, nearest = 1) {
  return (Math.round(value / nearest) * nearest + 360) % 360;
}

function directionTrend(start, end) {
  const diff = ((end - start + 540) % 360) - 180;
  if (diff > 10) return `veering right by ${Math.round(diff)} degrees`;
  if (diff < -10) return `backing left by ${Math.round(Math.abs(diff))} degrees`;
  return "mostly oscillatory with little net trend";
}

function mean(values) {
  const valid = values.filter((value) => Number.isFinite(value));
  if (!valid.length) return 0;
  return valid.reduce((total, value) => total + value, 0) / valid.length;
}

function pstdev(values) {
  const avg = mean(values);
  return Math.sqrt(mean(values.map((value) => (value - avg) ** 2)));
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function padDir(value) {
  return String(Math.round(value)).padStart(3, "0");
}

function capitalize(value) {
  return String(value).charAt(0).toUpperCase() + String(value).slice(1);
}

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function selectedCompareModels() {
  return [...compareModels.querySelectorAll("input:checked")].map((input) => input.value);
}

function waitForReportImages(timeoutMs = 5000) {
  const frameDocument = reportFrame.contentDocument;
  if (!frameDocument) return Promise.resolve();
  const images = [...frameDocument.images];
  if (!images.length) return Promise.resolve();
  const imagePromises = images.map((image) => {
    if (image.complete && image.naturalWidth > 0) return Promise.resolve();
    return new Promise((resolve) => {
      image.addEventListener("load", resolve, { once: true });
      image.addEventListener("error", resolve, { once: true });
    });
  });
  return Promise.race([Promise.all(imagePromises), new Promise((resolve) => setTimeout(resolve, timeoutMs))]);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
