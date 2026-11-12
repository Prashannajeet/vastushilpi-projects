from __future__ import annotations

import json
from pathlib import Path


DEPLOY_STATIC = Path(__file__).parent / "mandideep_streamlit_vr" / "static"
OUTPUT = DEPLOY_STATIC / "mandideep_embedded_map.html"


def build_embedded_map() -> None:
    """Create a self-contained map HTML for Streamlit local-file embedding."""
    html = (DEPLOY_STATIC / "mandideep_aoi_3d_buildings.html").read_text(encoding="utf-8")
    source_files = {
        "mandideep_aoi_wgs84.geojson": "mandideep_aoi_wgs84.geojson",
        "mandideep_aoi_buffer_100m_wgs84.geojson": "mandideep_aoi_buffer_100m_wgs84.geojson",
        "lines_aoi_wgs84.geojson": "lines_aoi_wgs84.geojson",
        "mandideep_overture_buildings_3d_wgs84.geojson": "mandideep_overture_buildings_3d_wgs84.geojson",
        "mandideep_tree_3d_wgs84.geojson": "mandideep_tree_3d_wgs84.geojson",
        "aoi_tree_polygon_wgs84.geojson": "aoi_tree_polygon_wgs84.geojson",
        "mandideep_satellite_tree_points_wgs84.geojson": "mandideep_tree_points_wgs84.geojson",
    }
    embedded = {
        requested_name: json.loads(
            (DEPLOY_STATIC / actual_name).read_text(encoding="utf-8")
        )
        for requested_name, actual_name in source_files.items()
    }
    marker = (
        "function addGeo(id,url){return fetch(url).then(r=>r.json()).then(data=>{"
        "map.addSource(id,{type:'geojson',data});return data;});}"
    )
    replacement = (
        "const EMBEDDED_SOURCES="
        + json.dumps(embedded, separators=(",", ":"))
        + "; function addGeo(id,url){const data=EMBEDDED_SOURCES[url];"
        "if(!data)return Promise.reject(new Error('Missing embedded source: '+url));"
        "map.addSource(id,{type:'geojson',data});return Promise.resolve(data);}"
    )
    if marker not in html:
        raise RuntimeError("map source loader marker was not found")
    html = html.replace(marker, replacement, 1)
    html = html.replace(
        "fetch('mandideep_satellite_tree_points_wgs84.geojson').then(r=>r.json()).then(data=>{",
        "Promise.resolve(EMBEDDED_SOURCES['mandideep_satellite_tree_points_wgs84.geojson']).then(data=>{",
        1,
    )
    OUTPUT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_embedded_map()
