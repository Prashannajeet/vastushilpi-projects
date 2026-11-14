"""Clip the bundled road lines to the Mandideep AOI and 100 m buffer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely.geometry import GeometryCollection, LineString, MultiLineString, mapping, shape
from shapely.ops import transform


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data"
ROADS_FILE = DATA_DIR / "mandideep_osm_roads_wgs84.geojson"
AOI_FILE = DATA_DIR / "mandideep_aoi_wgs84.geojson"
BUFFER_FILE = DATA_DIR / "mandideep_aoi_buffer_100m_wgs84.geojson"
EXACT_OUTPUT = DATA_DIR / "mandideep_osm_roads_aoi_wgs84.geojson"
BUFFER_OUTPUT = DATA_DIR / "mandideep_osm_roads_buffer100m_wgs84.geojson"
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
TO_WGS84 = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform


def read_geojson(path: Path) -> dict[str, Any]:
    """Read a UTF-8 GeoJSON FeatureCollection."""
    return json.loads(path.read_text(encoding="utf-8"))


def line_parts(geometry: Any) -> list[LineString]:
    """Return only line components from a clipped Shapely geometry."""
    if isinstance(geometry, LineString):
        return [geometry] if not geometry.is_empty and geometry.length > 0 else []
    if isinstance(geometry, MultiLineString):
        return [part for part in geometry.geoms if not part.is_empty and part.length > 0]
    if isinstance(geometry, GeometryCollection):
        return [part for item in geometry.geoms for part in line_parts(item)]
    return []


def clip(scope_path: Path, scope_name: str) -> tuple[dict[str, Any], int]:
    """Clip road lines to a scope polygon using UTM Zone 43N."""
    roads = read_geojson(ROADS_FILE)
    scope = read_geojson(scope_path)
    scope_geom = transform(TO_UTM, shape(scope["features"][0]["geometry"]))
    features: list[dict[str, Any]] = []
    source_count = 0
    for source in roads.get("features", []):
        source_geom = transform(TO_UTM, shape(source["geometry"]))
        clipped = source_geom.intersection(scope_geom)
        parts = line_parts(clipped)
        if not parts:
            continue
        source_count += 1
        for part_index, part in enumerate(parts):
            properties = dict(source.get("properties") or {})
            properties["clip_scope"] = scope_name
            properties["clip_part"] = part_index
            features.append({"type": "Feature", "geometry": mapping(transform(TO_WGS84, part)), "properties": properties})
    output = {
        "type": "FeatureCollection",
        "name": f"Mandideep road lines clipped to {scope_name}",
        "metadata": {
            "source": "OpenStreetMap contributors",
            "source_file": ROADS_FILE.name,
            "clip_scope": scope_name,
            "analysis_crs": "EPSG:32643 / UTM Zone 43N",
            "display_crs": "EPSG:4326",
        },
        "features": features,
    }
    return output, source_count


def main() -> None:
    """Write exact-AOI and 100 m-buffer clipped road layers."""
    outputs = ((AOI_FILE, "exact AOI", EXACT_OUTPUT), (BUFFER_FILE, "100 m buffer", BUFFER_OUTPUT))
    for scope_path, scope_name, output_path in outputs:
        result, source_count = clip(scope_path, scope_name)
        output_path.write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
        print(f"{output_path.name}: {len(result['features'])} output parts from {source_count} source roads")


if __name__ == "__main__":
    main()
