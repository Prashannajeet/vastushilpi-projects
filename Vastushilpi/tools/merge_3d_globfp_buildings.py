"""Merge 3D-GloBFP footprints into the Mandideep building layer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyogrio
from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parent.parent / "mandideep_webgis"
DATA_DIR = ROOT / "public" / "data"
REPOSITORY = Path(r"D:\Project\Development\Data Repository\3D-GloBFP_India")
TILE = REPOSITORY / "tiles_zip" / "1821_77.5_22.5_78.75_23.75_IN.zip"
AOI_BUFFER = DATA_DIR / "mandideep_aoi_buffer_100m_wgs84.geojson"
CURRENT_BUILDINGS = DATA_DIR / "mandideep_overture_buildings_3d_wgs84.geojson"
OUTPUT = DATA_DIR / "mandideep_buildings_merged_3d_wgs84.geojson"
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
TO_WGS84 = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform
MAX_DISPLAY_HEIGHT_M = 60.0


def tile_path() -> str:
    """Return the GDAL virtual path to the GloBFP Shapefile."""
    return f"/vsizip/{TILE.as_posix()}/{TILE.stem}.shp"


def read_current() -> tuple[list[dict[str, Any]], Any]:
    """Read and clip current buildings to the updated 100 m buffer."""
    buffer_data = json.loads(AOI_BUFFER.read_text(encoding="utf-8"))
    buffer_wgs84 = shape(buffer_data["features"][0]["geometry"])
    buffer_utm = transform(TO_UTM, buffer_wgs84)
    result: list[dict[str, Any]] = []
    for feature in json.loads(CURRENT_BUILDINGS.read_text(encoding="utf-8"))["features"]:
        source = shape(feature["geometry"])
        projected = transform(TO_UTM, source)
        if not projected.intersects(buffer_utm):
            continue
        clipped = projected.intersection(buffer_utm)
        if clipped.is_empty:
            continue
        result.append({"feature": feature, "geometry": clipped})
    return result, buffer_utm


def main() -> None:
    """Write a deduplicated WGS 84 merged building layer."""
    current, buffer_utm = read_current()
    current_geometries = [item["geometry"] for item in current]
    current_tree = STRtree(current_geometries)
    minx, miny, maxx, maxy = transform(TO_WGS84, buffer_utm).bounds
    glo = pyogrio.read_dataframe(tile_path(), bbox=(minx, miny, maxx, maxy), columns=["Height"])
    glo = glo.to_crs("EPSG:32643")
    features: list[dict[str, Any]] = []
    for item in current:
        projected = item["geometry"]
        feature = item["feature"]
        feature["geometry"] = mapping(transform(TO_WGS84, projected))
        features.append(feature)

    added = 0
    for index, row in enumerate(glo.itertuples(index=False)):
        projected = row.geometry
        if projected.is_empty or not projected.intersects(buffer_utm):
            continue
        candidates = current_tree.query(projected, predicate="intersects")
        overlap = max((projected.intersection(current_geometries[candidate]).area / max(projected.area, 1e-12) for candidate in candidates), default=0)
        if overlap > 0.25:
            continue
        clipped = projected.intersection(buffer_utm)
        if clipped.is_empty:
            continue
        height = float(row.Height) if row.Height == row.Height else 6.0
        display_height = max(3.0, min(height, MAX_DISPLAY_HEIGHT_M))
        feature = {
            "type": "Feature",
            "geometry": mapping(transform(TO_WGS84, clipped)),
            "properties": {
                "building_id": f"globfp-{index}",
                "source_dataset": "3D-GloBFP India",
                "source": "3D-GloBFP India tile 1821",
                "source_height_m": height,
                "height_m": display_height,
                "display_height_m": display_height,
                "height_source": "3D-GloBFP Height",
                "height_model": "source height capped at 60 m for web visualization",
                "source_confidence": "not provided",
            },
        }
        features.append(feature)
        added += 1

    output = {
        "type": "FeatureCollection",
        "name": "Mandideep merged 3D building footprints",
        "metadata": {
            "sources": ["Overture/ML current building layer", "3D-GloBFP India"],
            "clip_scope": "updated AOI plus 100 m buffer",
            "analysis_crs": "EPSG:32643 / UTM Zone 43N",
            "display_crs": "EPSG:4326",
            "deduplication": "GloBFP feature omitted when more than 25% overlaps a current footprint",
        },
        "features": features,
    }
    OUTPUT.write_text(json.dumps(output, separators=(",", ":")), encoding="utf-8")
    print(f"Current clipped buildings: {len(current):,}")
    print(f"GloBFP additions: {added:,}")
    print(f"Merged output: {len(features):,}")
    print(f"Wrote: {OUTPUT}")


if __name__ == "__main__":
    main()
