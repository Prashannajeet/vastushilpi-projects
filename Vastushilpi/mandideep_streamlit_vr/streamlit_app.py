from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import geopandas as gpd
import streamlit as st
import streamlit.components.v1 as components


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
VR_URL = "https://prashannajeet.github.io/vastushilpi-projects/Vastushilpi/mandideep_streamlit_vr/docs/mandideep_aoi_vr.html"

st.set_page_config(page_title="Mandideep AOI Web GIS", page_icon="🗺️", layout="wide")
st.title("Mandideep AOI — Web GIS")
st.caption("Satellite imagery, UTM 43N-derived vectors, 3D buildings, and tree inventory")

with st.spinner("Reading spatial layers…"):
    aoi = gpd.read_file(DATA_DIR / "aoi_tree_polygon_wgs84.geojson")
    trees = gpd.read_file(DATA_DIR / "mandideep_tree_points_wgs84.geojson")
    buildings = gpd.read_file(DATA_DIR / "mandideep_overture_buildings_3d_wgs84.geojson")
    lines = gpd.read_file(DATA_DIR / "lines_aoi_wgs84.geojson")

cols = st.columns(4)
cols[0].metric("AOI area", f"{aoi.to_crs(32643).area.sum() / 1_000_000:.2f} km²")
cols[1].metric("Tree points", f"{len(trees):,}")
cols[2].metric("3D buildings", f"{len(buildings):,}")
cols[3].metric("Vector features", f"{len(lines):,}")

st.subheader("Viewers")
st.link_button("Open optional WebXR / VR view", VR_URL)


def inline_map_data(html: str) -> str:
    """Replace relative GeoJSON fetches with embedded data URLs for Streamlit."""
    filenames = [
        "mandideep_aoi_wgs84.geojson",
        "mandideep_aoi_buffer_100m_wgs84.geojson",
        "lines_aoi_wgs84.geojson",
        "mandideep_overture_buildings_3d_wgs84.geojson",
        "mandideep_tree_3d_wgs84.geojson",
        "aoi_tree_polygon_wgs84.geojson",
        "mandideep_tree_points_wgs84.geojson",
    ]
    for filename in filenames:
        source = DATA_DIR / filename
        if source.exists():
            data_url = "data:application/json," + quote(source.read_text(encoding="utf-8"))
            html = html.replace(f"'{filename}'", f"'{data_url}'")
    return html


st.subheader("Main map")
desktop_map = DATA_DIR / "mandideep_aoi_3d_buildings.html"
if desktop_map.exists():
    components.html(inline_map_data(desktop_map.read_text(encoding="utf-8")), height=820, scrolling=False)
else:
    st.error("Desktop map HTML is missing from the deployment package.")

st.subheader("Layer inventory")
st.dataframe(
    {
        "Layer": ["AOI tree polygon", "Satellite tree points", "3D buildings", "CAD/vector linework"],
        "Features": [len(aoi), len(trees), len(buildings), len(lines)],
        "CRS": ["WGS 84 display", "WGS 84 display", "WGS 84 display", "WGS 84 display"],
        "Source": ["AOI Tree.kmz", "ArcGIS World Imagery detection", "Overture Maps", "CAD Shape files"],
    },
    hide_index=True,
    use_container_width=True,
)

st.caption("Analysis CRS: EPSG:32643 / UTM Zone 43N. Display CRS: EPSG:4326. Satellite imagery: ArcGIS World Imagery.")
