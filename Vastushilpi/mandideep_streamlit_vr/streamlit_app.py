from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
VR_URL = "https://prashannajeet.github.io/vastushilpi-projects/Vastushilpi/mandideep_streamlit_vr/docs/mandideep_aoi_vr.html"

st.set_page_config(page_title="Mandideep AOI VR", page_icon="🌳", layout="wide")
st.title("Mandideep AOI — GIS and VR viewer")
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
left, right = st.columns(2)
with left:
    st.link_button("Open standalone WebXR / VR viewer", VR_URL, use_container_width=True)
    st.info("Open the standalone viewer on a headset for WebXR. Streamlit remains the data and analysis dashboard.")
with right:
    local_map = APP_DIR / "data" / "mandideep_aoi_3d_buildings.html"
    if local_map.exists():
        st.download_button("Download desktop map HTML", local_map.read_bytes(), local_map.name, "text/html", use_container_width=True)

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
