from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FILES = (
    "mandideep_aoi_wgs84.geojson",
    "mandideep_aoi_buffer_100m_wgs84.geojson",
    "mandideep_overture_buildings_3d_wgs84.geojson",
    "mandideep_tree_3d_wgs84.geojson",
    "mandideep_tree_points_wgs84.geojson",
    "aoi_tree_polygon_wgs84.geojson",
)


def test_all_layers_are_bundled_and_valid() -> None:
    for filename in FILES:
        with (DATA / filename).open(encoding="utf-8") as handle:
            payload = json.load(handle)
        assert payload["type"] == "FeatureCollection"
        assert isinstance(payload["features"], list)


def test_active_map_does_not_reference_removed_layers() -> None:
    source = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    assert "CAD/vector linework" not in source
    assert "Contours" not in source
    assert "Feature labels" not in source

