from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherModel:
    provider: str
    model_id: str
    label: str
    region: str
    selectable: bool = True


AUTO_PRIMARY_MODEL = "auto_highest_resolution"

HIGHEST_RESOLUTION_MODEL_ORDER: tuple[str, ...] = (
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
)


OPEN_METEO_MODELS: tuple[WeatherModel, ...] = (
    WeatherModel("Open-Meteo", AUTO_PRIMARY_MODEL, "Highest resolution available", "Automatic"),
    WeatherModel("Open-Meteo", "best_match", "Best match", "Automatic"),
    WeatherModel("ECMWF", "ecmwf_ifs", "ECMWF IFS HRES 9 km", "Global"),
    WeatherModel("ECMWF", "ecmwf_ifs025", "ECMWF IFS 0.25 deg", "Global"),
    WeatherModel("ECMWF", "ecmwf_aifs025_single", "ECMWF AIFS 0.25 deg single", "Global"),
    WeatherModel("CMA", "cma_grapes_global", "CMA GRAPES global", "Global"),
    WeatherModel("BOM", "bom_access_global", "BOM ACCESS global", "Global"),
    WeatherModel("NCEP", "gfs_seamless", "NCEP GFS seamless", "Global"),
    WeatherModel("NCEP", "gfs_global", "NCEP GFS global 0.11/0.25 deg", "Global"),
    WeatherModel("NCEP", "gfs_hrrr", "NCEP HRRR U.S. CONUS", "United States"),
    WeatherModel("NCEP", "ncep_nbm_conus", "NCEP NBM U.S. CONUS", "United States"),
    WeatherModel("NCEP", "ncep_nam_conus", "NCEP NAM U.S. CONUS", "United States"),
    WeatherModel("NCEP", "gfs_graphcast025", "NCEP GFS GraphCast", "Global"),
    WeatherModel("NCEP", "ncep_aigfs025", "NCEP AIGFS 0.25 deg", "Global"),
    WeatherModel("NCEP", "ncep_hgefs025_ensemble_mean", "NCEP HGEFS 0.25 deg ensemble mean", "Global"),
    WeatherModel("JMA", "jma_seamless", "JMA seamless", "Automatic / Japan-global"),
    WeatherModel("JMA", "jma_msm", "JMA MSM", "Japan region"),
    WeatherModel("JMA", "jma_gsm", "JMA GSM", "Global"),
    WeatherModel("KMA", "kma_seamless", "KMA seamless", "Automatic / Korea-global"),
    WeatherModel("KMA", "kma_ldps", "KMA LDPS", "Korea region"),
    WeatherModel("KMA", "kma_gdps", "KMA GDPS", "Global"),
    WeatherModel("DWD", "icon_seamless", "DWD ICON seamless", "Automatic / Europe-global"),
    WeatherModel("DWD", "icon_global", "DWD ICON global", "Global"),
    WeatherModel("DWD", "icon_eu", "DWD ICON EU", "Europe"),
    WeatherModel("DWD", "icon_d2", "DWD ICON D2", "Central Europe"),
    WeatherModel("GEM", "gem_seamless", "GEM seamless", "Automatic / Canada-global"),
    WeatherModel("GEM", "gem_global", "GEM global", "Global"),
    WeatherModel("GEM", "gem_regional", "GEM regional", "North America"),
    WeatherModel("GEM", "gem_hrdps_continental", "GEM HRDPS continental", "Canada region"),
    WeatherModel("GEM", "gem_hrdps_west", "GEM HRDPS west", "Western Canada"),
    WeatherModel("Meteo-France", "meteofrance_seamless", "Meteo-France seamless", "Automatic / Europe"),
    WeatherModel("Open-Meteo", "meteofrance_arpege_world", "Meteo-France ARPEGE world", "Global"),
    WeatherModel("Open-Meteo", "meteofrance_arpege_europe", "Meteo-France ARPEGE Europe", "Europe"),
    WeatherModel("Open-Meteo", "meteofrance_arome_france", "Meteo-France AROME France", "France region"),
    WeatherModel("Open-Meteo", "meteofrance_arome_france_hd", "Meteo-France AROME France HD", "France region"),
    WeatherModel("ItaliaMeteo", "italia_meteo_arpae_icon_2i", "ItaliaMeteo ARPAE ICON 2I", "Italy region"),
    WeatherModel("MET Norway", "metno_seamless", "MET Norway Nordic seamless (with ECMWF)", "Nordic region"),
    WeatherModel("MET Norway", "metno_nordic", "MET Norway Nordic", "Nordic region"),
    WeatherModel("KNMI", "knmi_seamless", "KNMI seamless (with ECMWF)", "Netherlands / Europe"),
    WeatherModel("KNMI", "knmi_harmonie_arome_europe", "KNMI Harmonie AROME Europe", "Europe"),
    WeatherModel("KNMI", "knmi_harmonie_arome_netherlands", "KNMI Harmonie AROME Netherlands", "Netherlands"),
    WeatherModel("DMI", "dmi_seamless", "DMI seamless (with ECMWF)", "Denmark / Europe"),
    WeatherModel("DMI", "dmi_harmonie_arome_europe", "DMI Harmonie AROME Europe", "Europe"),
    WeatherModel("UK Met Office", "ukmo_seamless", "UK Met Office seamless", "Automatic / UK-global"),
    WeatherModel("UK Met Office", "ukmo_global_deterministic_10km", "UK Met Office global 10 km", "Global"),
    WeatherModel("UK Met Office", "ukmo_uk_deterministic_2km", "UK Met Office UK 2 km", "UK region"),
    WeatherModel("MeteoSwiss", "meteoswiss_icon_seamless", "MeteoSwiss ICON seamless", "Switzerland region"),
    WeatherModel("MeteoSwiss", "meteoswiss_icon_ch1", "MeteoSwiss ICON CH1", "Switzerland region"),
    WeatherModel("MeteoSwiss", "meteoswiss_icon_ch2", "MeteoSwiss ICON CH2", "Switzerland region"),
    WeatherModel("GeoSphere", "geosphere_seamless", "GeoSphere seamless (with ECMWF)", "Austria region"),
    WeatherModel("GeoSphere", "geosphere_arome_austria", "GeoSphere AROME Austria", "Austria region"),
)


WINDY_POINT_FORECAST_MODELS: tuple[WeatherModel, ...] = (
    WeatherModel("Windy", "arome", "Meteo-France AROME", "France and nearby areas", selectable=False),
    WeatherModel("Windy", "aromeFrance", "Meteo-France AROME France", "Metropolitan France", selectable=False),
    WeatherModel("Windy", "gfs", "GFS", "Global", selectable=False),
    WeatherModel("Windy", "icon", "ICON global", "Global", selectable=False),
    WeatherModel("Windy", "iconEu", "ICON Europe", "Europe", selectable=False),
)


def model_payload() -> dict[str, object]:
    return {
        "open_meteo": [model.__dict__ for model in OPEN_METEO_MODELS],
        "windy_point_forecast": [model.__dict__ for model in WINDY_POINT_FORECAST_MODELS],
        "default_primary": AUTO_PRIMARY_MODEL,
        "default_compare": [
            "gfs_seamless",
            "ecmwf_ifs025",
            "meteofrance_seamless",
            "ukmo_seamless",
        ],
    }
