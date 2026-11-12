"""Fresh, self-contained Streamlit deployment for the Mandideep Web GIS."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


APP_VERSION = "mandideep-fresh-2026-11-12"
APP_DIR = Path(__file__).resolve().parent
MAP_DIR = APP_DIR / "app"
DATA_DIR = APP_DIR / "data"
DATA_FILES = (
    "mandideep_aoi_wgs84.geojson",
    "mandideep_aoi_buffer_100m_wgs84.geojson",
    "mandideep_overture_buildings_3d_wgs84.geojson",
    "mandideep_tree_3d_wgs84.geojson",
    "mandideep_tree_points_wgs84.geojson",
    "aoi_tree_polygon_wgs84.geojson",
)


def load_data() -> tuple[dict[str, Any], dict[str, int]]:
    """Load and validate every local GeoJSON layer before rendering the map."""
    payload: dict[str, Any] = {}
    counts: dict[str, int] = {}
    for filename in DATA_FILES:
        path = DATA_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing bundled layer: {filename}")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
            raise ValueError(f"Invalid GeoJSON FeatureCollection: {filename}")
        payload[filename] = data
        counts[filename] = len(data["features"])
    return payload, counts


def build_component(payload: dict[str, Any]) -> str:
    """Build a fully self-contained MapLibre iframe with local data embedded."""
    index = (MAP_DIR / "index.html").read_text(encoding="utf-8")
    body = index.split("<body>", 1)[1].split("</body>", 1)[0]
    css = (MAP_DIR / "app.css").read_text(encoding="utf-8")
    maplibre_css = (MAP_DIR / "vendor" / "maplibre-gl.css").read_text(encoding="utf-8")
    maplibre_js = (MAP_DIR / "vendor" / "maplibre-gl.js").read_text(encoding="utf-8")
    app_js = (MAP_DIR / "app.js").read_text(encoding="utf-8")
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.IGNORECASE | re.DOTALL)
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>{css}\n{maplibre_css}</style></head>
<body>{body}
<script>window.MANDIDEEP_INLINE_DATA={payload_json};window.MANDIDEEP_APP_VERSION="{APP_VERSION}";</script>
<script>{maplibre_js}</script>
<script>{app_js}</script>
</body></html>"""


st.set_page_config(page_title="Mandideep Web GIS", layout="wide", initial_sidebar_state="collapsed")

try:
    payload, counts = load_data()
    component = build_component(payload)
except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
    st.error(f"Mandideep map could not start: {error}")
    st.stop()

st.markdown(
    """
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
    [data-testid="stMainBlockContainer"], .block-container { max-width: none !important; padding: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(component, height=1000, scrolling=False)

