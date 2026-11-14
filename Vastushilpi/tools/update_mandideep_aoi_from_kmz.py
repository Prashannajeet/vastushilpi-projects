"""Update the Mandideep AOI and 100 m buffer from the approved KMZ."""

from __future__ import annotations

import json
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from pyproj import Transformer
from shapely.geometry import Polygon, mapping
from shapely.ops import transform


ROOT = Path(__file__).resolve().parent.parent / "mandideep_webgis"
DATA_DIR = ROOT / "public" / "data"
KMZ = ROOT.parent / "AOI Mandideep.kmz"
AOI_OUTPUT = DATA_DIR / "mandideep_aoi_wgs84.geojson"
BUFFER_OUTPUT = DATA_DIR / "mandideep_aoi_buffer_100m_wgs84.geojson"
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
TO_WGS84 = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform


def read_kmz_polygon() -> Polygon:
    """Read the first KML polygon from the approved KMZ."""
    namespace = {"k": "http://www.opengis.net/kml/2.2"}
    with zipfile.ZipFile(KMZ) as archive:
        root = ET.fromstring(archive.read("doc.kml"))
    text = root.find(".//k:Polygon/k:outerBoundaryIs/k:LinearRing/k:coordinates", namespace).text
    return Polygon([tuple(map(float, value.split(",")[:2])) for value in text.split()])


def collection(name: str, geometry: Polygon, area_m2: float, source: str) -> dict:
    """Create a versioned WGS 84 GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "name": name,
        "metadata": {"source": source, "updated": date.today().isoformat(), "analysis_crs": "EPSG:32643 / UTM Zone 43N", "display_crs": "EPSG:4326"},
        "features": [{"type": "Feature", "geometry": mapping(geometry), "properties": {"aoi_id": "mandideep_aoi", "area_m2": area_m2, "source": "AOI Mandideep.kmz"}}],
    }


def main() -> None:
    """Write the approved AOI and its metric 100 m buffer."""
    aoi = read_kmz_polygon()
    projected = transform(TO_UTM, aoi)
    buffer = transform(TO_WGS84, projected.buffer(100))
    AOI_OUTPUT.write_text(json.dumps(collection("Mandideep updated AOI", aoi, projected.area, KMZ.name), separators=(",", ":")), encoding="utf-8")
    BUFFER_OUTPUT.write_text(json.dumps(collection("Mandideep updated AOI 100 m buffer", buffer, transform(TO_UTM, buffer).area, KMZ.name), separators=(",", ":")), encoding="utf-8")
    print(f"AOI area: {projected.area / 1e6:.3f} km2")
    print(f"AOI bounds: {aoi.bounds}")
    print(f"Buffer bounds: {buffer.bounds}")


if __name__ == "__main__":
    main()
