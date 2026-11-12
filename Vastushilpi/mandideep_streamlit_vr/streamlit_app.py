"""Streamlit-hosted Mandideep Web GIS.

The map is embedded as a Streamlit custom component with its GeoJSON payload
injected into the component. This avoids file:// fetches, GitHub Pages, and
Streamlit static-file routing while keeping Streamlit as the main app.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


APP_BUILD = "mandideep-streamlit-inline-map-2026-11-12"
PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
MAP_DIR = PACKAGE_DIR.parent / "mandideep_webgis"
DATA_FILES = (
    "mandideep_aoi_wgs84.geojson",
    "mandideep_aoi_buffer_100m_wgs84.geojson",
    "lines_aoi_wgs84.geojson",
    "mandideep_overture_buildings_3d_wgs84.geojson",
    "mandideep_tree_3d_wgs84.geojson",
    "mandideep_tree_points_wgs84.geojson",
    "aoi_tree_polygon_wgs84.geojson",
)


@st.cache_data(show_spinner=False)
def load_geojson_payload() -> dict[str, Any]:
    """Load and cache the display GeoJSON payload for the map component."""
    payload: dict[str, Any] = {}
    for name in DATA_FILES:
        path = DATA_DIR / name
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                payload[name] = json.load(handle)
    return payload


@st.cache_data(show_spinner=False)
def build_map_component(payload_json: str, body: str, css: str, maplibre_css: str, app_js: str) -> str:
    """Build one self-contained HTML component from cached source inputs."""
    safe_payload = payload_json.replace("</", "<\\/")
    body_without_scripts = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.IGNORECASE | re.DOTALL)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>{css}\n{maplibre_css}</style></head>
<body>{body_without_scripts}
<script>window.MANDIDEEP_INLINE_DATA={safe_payload};</script>
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script>{app_js}</script>
</body></html>"""


def read_map_source() -> tuple[str, str, str, str]:
    """Read the static map shell and its local source assets."""
    index = (MAP_DIR / "index.html").read_text(encoding="utf-8")
    body = index.split("<body>", 1)[1].split("</body>", 1)[0]
    css = (MAP_DIR / "app.css").read_text(encoding="utf-8")
    maplibre_css = (MAP_DIR / "public" / "vendor" / "maplibre-gl.css").read_text(encoding="utf-8")
    app_js = (MAP_DIR / "app.js").read_text(encoding="utf-8")
    return body, css, maplibre_css, app_js


st.set_page_config(page_title="Mandideep Web GIS", layout="wide", initial_sidebar_state="collapsed")
payload = load_geojson_payload()

with st.sidebar:
    st.title("Mandideep Web GIS")
    st.caption("Streamlit-hosted main map")
    st.success("Map data embedded and ready")
    st.metric("Tree points", f"{len(payload.get('mandideep_tree_points_wgs84.geojson', {}).get('features', [])):,}")
    st.metric("3D buildings", f"{len(payload.get('mandideep_overture_buildings_3d_wgs84.geojson', {}).get('features', [])):,}")
    st.metric("CAD/vector features", f"{len(payload.get('lines_aoi_wgs84.geojson', {}).get('features', [])):,}")
    st.caption("Analysis CRS: EPSG:32643 / UTM Zone 43N\nDisplay CRS: EPSG:4326")
    st.divider()
    st.markdown("**Vastushilpi Projects & Consultants Pvt. Ltd.**")
    st.markdown(
        "[E-4/86 Arera Colony, 10 No. Market, Arera Colony, Bhopal, Madhya Pradesh 462016](https://www.google.com/search?q=vastushilpi+projects+%26+consultants+pvt.+ltd.+address)"
    )
    st.markdown("Phone: [0755 276 3138](tel:+917552763138)")

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
    [data-testid="stMainBlockContainer"], .block-container { max-width: none !important; padding: 0 !important; }
    [data-testid="stHeader"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

body, css, maplibre_css, app_js = read_map_source()
component = build_map_component(
    json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
    body,
    css,
    maplibre_css,
    app_js,
)
components.html(component, height=1000, scrolling=False)
