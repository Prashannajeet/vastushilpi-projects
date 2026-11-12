"""Mandideep analysis dashboard.

The main map is intentionally hosted as a standalone static Web GIS. This
Streamlit app provides data inventory and analysis context without embedding
the large WebGL/GeoJSON map inside Streamlit.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st


APP_BUILD = "mandideep-analysis-dashboard-2026-11-12"
PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
MAIN_MAP_URL = os.getenv(
    "MANDIDEEP_WEBGIS_URL",
    "https://prashannajeet.github.io/vastushilpi-projects/",
)


@st.cache_data(show_spinner=False)
def read_geojson_summary(path: str) -> dict[str, Any]:
    """Read a GeoJSON file and return a small inventory summary."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    features = document.get("features", [])
    return {
        "name": file_path.name,
        "features": len(features),
        "geometry_types": sorted(
            {
                feature.get("geometry", {}).get("type", "Unknown")
                for feature in features
                if feature.get("geometry")
            }
        ),
    }


def available_summary() -> list[dict[str, Any]]:
    """Return summaries for the published Mandideep data layers."""
    files = [
        "mandideep_aoi_wgs84.geojson",
        "mandideep_aoi_buffer_100m_wgs84.geojson",
        "lines_aoi_wgs84.geojson",
        "mandideep_overture_buildings_3d_wgs84.geojson",
        "mandideep_tree_3d_wgs84.geojson",
        "mandideep_tree_points_wgs84.geojson",
    ]
    return [
        read_geojson_summary(str(DATA_DIR / name))
        for name in files
        if (DATA_DIR / name).exists()
    ]


st.set_page_config(page_title="Mandideep Analysis Dashboard", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main { padding-top: 1.5rem; }
    .map-link { padding: 1rem; border: 1px solid #b8d8d0; border-radius: .5rem; background: #eefaf6; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Mandideep Analysis Dashboard")
st.caption("Data inventory and analysis context · the main map is hosted separately")

st.markdown('<div class="map-link">', unsafe_allow_html=True)
st.subheader("Main Mandideep Web GIS")
st.write("Open the standalone MapLibre application for satellite imagery, terrain, vectors, trees and 3D buildings.")
st.link_button("Open Main Map", MAIN_MAP_URL, type="primary")
st.markdown("</div>", unsafe_allow_html=True)

summaries = available_summary()
by_name = {item["name"]: item for item in summaries}
building_count = by_name.get("mandideep_overture_buildings_3d_wgs84.geojson", {}).get("features", 0)
tree_count = by_name.get("mandideep_tree_points_wgs84.geojson", {}).get("features", 0)
vector_count = by_name.get("lines_aoi_wgs84.geojson", {}).get("features", 0)
aoi_features = by_name.get("mandideep_aoi_wgs84.geojson", {}).get("features", 0)

st.subheader("Data status")
metric_columns = st.columns(4)
metric_columns[0].metric("AOI features", f"{aoi_features:,}")
metric_columns[1].metric("Tree points", f"{tree_count:,}")
metric_columns[2].metric("3D buildings", f"{building_count:,}")
metric_columns[3].metric("CAD/vector features", f"{vector_count:,}")

st.subheader("Layer inventory")
if summaries:
    rows = [
        {
            "Layer": item["name"],
            "Features": item["features"],
            "Geometry": ", ".join(item["geometry_types"]) or "Unknown",
            "Display CRS": "WGS 84 / EPSG:4326",
        }
        for item in summaries
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.error(f"No prepared layers were found in {DATA_DIR}.")

st.info(
    "Analysis CRS: EPSG:32643 / UTM Zone 43N. Display CRS: EPSG:4326. "
    "The standalone map loads local GeoJSON through HTTP and should not be opened with file://."
)

with st.expander("Architecture"):
    st.markdown(
        "- **Main map:** standalone static Web GIS in `Vastushilpi/mandideep_webgis`.\n"
        "- **Analysis:** this Streamlit inventory/dashboard.\n"
        "- **Rendering:** MapLibre with ArcGIS Satellite default basemap.\n"
        "- **Heavy layer:** 3D buildings are loaded by the standalone map in the background."
    )
