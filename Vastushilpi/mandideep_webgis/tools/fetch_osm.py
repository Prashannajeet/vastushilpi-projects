"""Fetch and convert a bounded OpenStreetMap extract for Mandideep Web GIS."""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
BBOX = (22.9938, 77.4494, 23.1167, 77.5807)  # south, west, north, east
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "data"
USER_AGENT = "Mandideep-Web-GIS/1.0 (OSM extract for project visualization)"


def fetch_overpass() -> dict[str, Any]:
    """Fetch OSM ways intersecting the project bounding box."""
    south, west, north, east = BBOX
    query = f"""[out:json][timeout:180];
(
  way[highway]({south},{west},{north},{east});
  way[railway]({south},{west},{north},{east});
  way[waterway]({south},{west},{north},{east});
  way[natural=water]({south},{west},{north},{east});
  way[landuse=reservoir]({south},{west},{north},{east});
  way[water=lake]({south},{west},{north},{east});
);
out geom tags;
"""
    payload = urlencode({"data": query}).encode("utf-8")
    request = Request(OVERPASS_URL, data=payload, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=240) as response:
        return json.load(response)


def feature(geometry_type: str, coordinates: Any, tags: dict[str, Any], osm_id: int) -> dict[str, Any]:
    """Build a GeoJSON feature with compact OSM properties."""
    properties = {"osm_id": osm_id, **tags}
    return {"type": "Feature", "geometry": {"type": geometry_type, "coordinates": coordinates}, "properties": properties}


def coordinates(element: dict[str, Any]) -> list[list[float]]:
    """Return an OSM way's coordinate pairs in display order."""
    return [[point["lon"], point["lat"]] for point in element.get("geometry", [])]


def collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a GeoJSON FeatureCollection with provenance metadata."""
    return {
        "type": "FeatureCollection",
        "name": "Mandideep OSM extract",
        "metadata": {"source": "OpenStreetMap contributors", "retrieved": date.today().isoformat(), "bbox": BBOX},
        "features": features,
    }


def write_outputs(payload: dict[str, Any]) -> dict[str, int]:
    """Split the OSM response into independently switchable GeoJSON layers."""
    roads: list[dict[str, Any]] = []
    railways: list[dict[str, Any]] = []
    waterways: list[dict[str, Any]] = []
    waterbodies: list[dict[str, Any]] = []

    for element in payload.get("elements", []):
        if element.get("type") != "way":
            continue
        coords = coordinates(element)
        if len(coords) < 2:
            continue
        tags = element.get("tags", {})
        osm_id = int(element["id"])
        if "highway" in tags:
            roads.append(feature("LineString", coords, {"layer": "roads", "class": tags["highway"], "name": tags.get("name", "")}, osm_id))
        if "railway" in tags:
            railways.append(feature("LineString", coords, {"layer": "railways", "class": tags["railway"], "name": tags.get("name", "")}, osm_id))
        if "waterway" in tags:
            waterways.append(feature("LineString", coords, {"layer": "waterways", "class": tags["waterway"], "name": tags.get("name", "")}, osm_id))
        waterbody = tags.get("natural") == "water" or tags.get("landuse") == "reservoir" or tags.get("water") == "lake" or tags.get("waterway") == "riverbank"
        if waterbody and coords[0] == coords[-1] and len(coords) >= 4:
            waterbodies.append(feature("Polygon", [coords], {"layer": "waterbodies", "class": tags.get("water", tags.get("natural", tags.get("landuse", "water"))), "name": tags.get("name", "")}, osm_id))

    outputs = {
        "mandideep_osm_roads_wgs84.geojson": roads,
        "mandideep_osm_railways_wgs84.geojson": railways,
        "mandideep_osm_waterways_wgs84.geojson": waterways,
        "mandideep_osm_waterbodies_wgs84.geojson": waterbodies,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, features in outputs.items():
        (OUTPUT_DIR / filename).write_text(json.dumps(collection(features), separators=(",", ":")), encoding="utf-8")
    return {key: len(value) for key, value in outputs.items()}


def main() -> None:
    """Fetch, split, and report the bounded OSM extract."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    counts = write_outputs(fetch_overpass())
    for filename, count in counts.items():
        logging.info("%s: %s features", filename, count)


if __name__ == "__main__":
    main()
