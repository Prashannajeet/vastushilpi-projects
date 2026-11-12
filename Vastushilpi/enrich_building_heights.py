"""Assign display heights to Mandideep buildings from footprint area.

The source building feed contains provisional heights for this AOI. This
repeatable enrichment keeps the source height fields and adds a visualization
height in the 6–30 m range. Larger footprints receive taller display heights
using a log-area scale, which reduces the influence of a few very large
industrial polygons while preserving the monotonic size relationship.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import shape


MIN_DISPLAY_HEIGHT_M = 6.0
MAX_DISPLAY_HEIGHT_M = 30.0
ANALYSIS_CRS = "EPSG:32643"
DATA_NAME = "mandideep_overture_buildings_3d_wgs84.geojson"


def enrich_buildings(input_path: Path, output_paths: list[Path]) -> dict[str, Any]:
    """Add footprint area and size-based display height to building features."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    geometries = [shape(feature["geometry"]) for feature in features]
    projected = gpd.GeoSeries(geometries, crs="EPSG:4326").to_crs(ANALYSIS_CRS)
    areas = [max(float(area), 0.0) for area in projected.area]
    log_areas = [math.log1p(area) for area in areas]
    low = min(log_areas) if log_areas else 0.0
    high = max(log_areas) if log_areas else 1.0
    span = high - low or 1.0

    for feature, area, log_area in zip(features, areas, log_areas):
        normalized = (log_area - low) / span
        display_height = MIN_DISPLAY_HEIGHT_M + normalized * (
            MAX_DISPLAY_HEIGHT_M - MIN_DISPLAY_HEIGHT_M
        )
        properties = feature.setdefault("properties", {})
        properties["footprint_area_m2"] = round(area, 2)
        properties["display_height_m"] = round(display_height, 2)
        properties["height_model"] = "log footprint area scaled 6–30 m"

    payload["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}}
    for output_path in output_paths:
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    return {
        "features": len(features),
        "area_min_m2": round(min(areas), 2) if areas else None,
        "area_max_m2": round(max(areas), 2) if areas else None,
        "height_min_m": MIN_DISPLAY_HEIGHT_M,
        "height_max_m": MAX_DISPLAY_HEIGHT_M,
        "output_count": len(output_paths),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    source = root / "mandideep_streamlit_vr" / "data" / DATA_NAME
    outputs = [
        source,
        root / "mandideep_webgis" / "public" / "data" / DATA_NAME,
    ]
    print(json.dumps(enrich_buildings(source, outputs), indent=2))
