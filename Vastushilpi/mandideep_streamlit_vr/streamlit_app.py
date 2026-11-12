from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
MAP_FILE = DATA_DIR / "mandideep_aoi_3d_buildings.html"

st.set_page_config(page_title="Mandideep Web GIS", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main { padding: 0 !important; }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    iframe { border: 0 !important; display: block; }
    </style>
    """,
    unsafe_allow_html=True,
)


def inline_map_data(html: str) -> str:
    """Embed the map's local GeoJSON files so it works inside Streamlit."""
    filenames = (
        "mandideep_aoi_wgs84.geojson",
        "mandideep_aoi_buffer_100m_wgs84.geojson",
        "lines_aoi_wgs84.geojson",
        "mandideep_overture_buildings_3d_wgs84.geojson",
        "mandideep_tree_3d_wgs84.geojson",
        "aoi_tree_polygon_wgs84.geojson",
        "mandideep_tree_points_wgs84.geojson",
    )
    for filename in filenames:
        source = DATA_DIR / filename
        if source.exists():
            payload = "data:application/json," + quote(source.read_text(encoding="utf-8"))
            html = html.replace(f"'{filename}'", f"'{payload}'")
    return html


if not MAP_FILE.exists():
    st.error("Mandideep map file is missing from the deployment package.")
else:
    components.html(inline_map_data(MAP_FILE.read_text(encoding="utf-8")), height=1000, scrolling=False)
