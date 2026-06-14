const state = {
  selectedVenue: null,
  selectedRaceArea: null,
  venueMarker: null,
  areaLayers: [],
  windLayer: null,
  windMaps: [],
  reportHtml: "",
  models: [],
  defaultCompareModels: [],
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
L.control.layers(
  { "OpenStreetMap": osmLayer },
  { "OpenSeaMap seamarks": openSeaMapLayer },
  { collapsed: false }
).addTo(map);

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

async function init() {
  setDefaultDate();
  await loadModelCatalog();
  statusEl.textContent = "Click the map or enter coordinates to set a custom venue.";
}

function setDefaultDate() {
  const dateInput = document.querySelector("input[name='date']");
  dateInput.value = new Date().toISOString().slice(0, 10);
}

async function loadModelCatalog() {
  const response = await fetch("/api/models");
  const catalog = await response.json();
  state.models = catalog.open_meteo || [];
  state.defaultCompareModels = catalog.default_compare || [];
  renderModelControls(catalog);
}

function renderModelControls(catalog) {
  modelSelect.innerHTML = state.models
    .filter((model) => model.selectable)
    .map((model) => (
      `<option value="${model.model_id}">${escapeHtml(model.label)} - ${escapeHtml(model.region)}</option>`
    ))
    .join("");
  modelSelect.value = catalog.default_primary || "auto_highest_resolution";
  compareModels.innerHTML = state.models
    .filter((model) => model.selectable)
    .map((model) => (
      `<label title="${escapeHtml(model.region)}"><input type="checkbox" value="${model.model_id}" ${state.defaultCompareModels.includes(model.model_id) ? "checked" : ""}>${escapeHtml(model.label)}</label>`
    ))
    .join("");
  const selectableCount = state.models.filter((model) => model.selectable).length;
  modelNote.textContent = `${selectableCount} Open-Meteo models available. Default comparison set is preselected.`;
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
  state.selectedVenue = {
    key,
    name: venueName.value || "Custom venue",
    latitude,
    longitude,
  };
  state.selectedRaceArea = {
    name: raceAreaName.value || "Race area",
    latitude,
    longitude,
    radius_nm: radiusNm,
  };
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
  state.venueMarker.bindPopup(`<strong>${escapeHtml(state.selectedVenue.name)}</strong>Drag marker or click map to move venue.`);
}

function renderRaceAreas() {
  state.areaLayers.forEach((layer) => layer.remove());
  state.areaLayers = [];
  if (!state.selectedVenue || !state.selectedRaceArea) {
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
  circle.bindPopup(`<strong>${escapeHtml(area.name)}</strong>${area.radius_nm} nm race area`);
  state.areaLayers.push(circle);
}

async function generateForecast(event) {
  event.preventDefault();
  if (!state.selectedVenue || !state.selectedRaceArea) {
    statusEl.textContent = "Click the map to set a venue first.";
    return;
  }
  statusEl.textContent = "Generating forecast...";
  printButton.disabled = true;
  const form = new FormData(event.currentTarget);
  const payload = {
    event: form.get("event"),
    team: form.get("team"),
    issue_time: form.get("issue_time"),
    synoptic_chart_url: form.get("synoptic_chart_url"),
    venue: {
      name: form.get("venue_name"),
      latitude: Number(form.get("latitude")),
      longitude: Number(form.get("longitude")),
      race_area_name: form.get("race_area_name"),
      race_radius_nm: Number(form.get("race_radius_nm")),
    },
    date: form.get("date"),
    start_hour: Number(form.get("start_hour")),
    end_hour: Number(form.get("end_hour")),
    forecast_days: Number(form.get("forecast_days") || 1),
    model: form.get("model"),
    area_map_mode: form.get("area_map_mode"),
    area_grid_size: Number(form.get("area_grid_size") || 15),
    compare_models: selectedCompareModels(),
  };
  try {
    const response = await fetch("/api/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await responseErrorMessage(response));
    }
    const result = await response.json();
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

function renderWindMapTimeOptions() {
  windMapTime.innerHTML = "";
  if (!state.windMaps.length) {
    windMapTime.disabled = true;
    windMapTime.innerHTML = "<option>No forecast</option>";
    return;
  }
  windMapTime.disabled = false;
  windMapTime.innerHTML = state.windMaps
    .map((windMap) => `<option value="${windMap.hour}">${escapeHtml(windMap.time_label)}</option>`)
    .join("");
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
  if (pointCount <= 81) {
    return 2;
  }
  if (pointCount <= 225) {
    return 3;
  }
  return 4;
}

function windBarbSvg(point) {
  const color = windSpeedColor(point.wind_speed_10m);
  const center = 26;
  const staffLength = 19;
  const radians = ((Number(point.wind_direction_10m) || 0) * Math.PI) / 180;
  const ux = Math.sin(radians);
  const uy = -Math.cos(radians);
  const x2 = center + ux * staffLength;
  const y2 = center + uy * staffLength;
  const barbAngle = radians + (120 * Math.PI) / 180;
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
  const markPath = marks.join(" ");
  const path = `M${center.toFixed(1)},${center.toFixed(1)} L${x2.toFixed(1)},${y2.toFixed(1)} ${markPath}`;
  return (
    `<svg class="selector-wind-barb-svg" viewBox="0 0 52 52" aria-hidden="true">` +
    `<path d="${path}" stroke="#172027" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.88"></path>` +
    `<path d="${path}" stroke="${color}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>` +
    `</svg>`
  );
}

function renderStreamlineOverlay(points, layer) {
  const seeds = points.filter((_, index) => index % 2 === 0);
  seeds.forEach((seed) => {
    const line = buildStreamline(seed, points);
    if (line.length < 2) {
      return;
    }
    const color = windSpeedColor(seed.wind_speed_10m);
    L.polyline(line, {
      color,
      weight: 3,
      opacity: 0.85,
      lineCap: "round",
      lineJoin: "round",
    }).addTo(layer);
    const end = line[line.length - 1];
    L.circleMarker(end, {
      radius: 3,
      color,
      fillColor: color,
      fillOpacity: 0.9,
      weight: 1,
    }).bindPopup(windPointPopup(seed)).addTo(layer);
  });
}

function buildStreamline(seed, points) {
  const latitudes = points.map((point) => Number(point.latitude));
  const longitudes = points.map((point) => Number(point.longitude));
  const latSpan = Math.max(...latitudes) - Math.min(...latitudes) || 0.01;
  const lonSpan = Math.max(...longitudes) - Math.min(...longitudes) || 0.01;
  const step = Math.min(latSpan, lonSpan) / 2.4;
  const line = [[Number(seed.latitude), Number(seed.longitude)]];
  let latitude = Number(seed.latitude);
  let longitude = Number(seed.longitude);
  for (let index = 0; index < 8; index += 1) {
    const nearest = nearestWindPoint(latitude, longitude, points);
    const direction = ((Number(nearest.wind_direction_10m) || 0) + 180) % 360;
    const radians = direction * Math.PI / 180;
    latitude += Math.cos(radians) * step;
    longitude += Math.sin(radians) * step / Math.max(0.2, Math.cos(latitude * Math.PI / 180));
    if (
      latitude < Math.min(...latitudes) || latitude > Math.max(...latitudes) ||
      longitude < Math.min(...longitudes) || longitude > Math.max(...longitudes)
    ) {
      break;
    }
    line.push([latitude, longitude]);
  }
  return line;
}

function nearestWindPoint(latitude, longitude, points) {
  return points.reduce((best, point) => {
    const bestDistance = Math.pow(best.latitude - latitude, 2) + Math.pow(best.longitude - longitude, 2);
    const distance = Math.pow(point.latitude - latitude, 2) + Math.pow(point.longitude - longitude, 2);
    return distance < bestDistance ? point : best;
  }, points[0]);
}

function windPointPopup(point) {
  const pressure = point.sea_level_pressure == null ? "n/a" : `${Math.round(point.sea_level_pressure)} hPa`;
  const cloud = point.cloud_cover == null ? "n/a" : `${Math.round(point.cloud_cover)}%`;
  return `<strong>Open-Meteo grid point</strong>TWD ${Math.round(point.wind_direction_10m)} | TWS ${Math.round(point.wind_speed_10m)} kt<br>Gust ${Math.round(point.wind_gust_10m)} kt | Cloud ${cloud}<br>Pressure ${pressure}`;
}

function windSpeedColor(speed) {
  const value = Number(speed) || 0;
  if (value >= 30) {
    return "rgb(112,48,160)";
  }
  if (value >= 25) {
    return "rgb(192,0,0)";
  }
  if (value >= 20) {
    return "rgb(255,0,0)";
  }
  if (value >= 15) {
    return "rgb(255,192,0)";
  }
  if (value >= 10) {
    return "rgb(255,255,0)";
  }
  if (value >= 5) {
    return "rgb(0,176,80)";
  }
  if (value >= 0.1) {
    return "rgb(0,112,192)";
  }
  return "#5a6670";
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function selectedCompareModels() {
  return [...compareModels.querySelectorAll("input:checked")].map((input) => input.value);
}

async function responseErrorMessage(response) {
  const text = await response.text();
  try {
    return JSON.parse(text).error || text || response.statusText;
  } catch {
    return text || response.statusText;
  }
}

function waitForReportImages(timeoutMs = 5000) {
  const frameDocument = reportFrame.contentDocument;
  if (!frameDocument) {
    return Promise.resolve();
  }
  const images = [...frameDocument.images];
  if (!images.length) {
    return Promise.resolve();
  }
  const imagePromises = images.map((image) => {
    if (image.complete && image.naturalWidth > 0) {
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      const done = () => resolve();
      image.addEventListener("load", done, { once: true });
      image.addEventListener("error", done, { once: true });
    });
  });
  return Promise.race([
    Promise.all(imagePromises),
    new Promise((resolve) => setTimeout(resolve, timeoutMs)),
  ]);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
