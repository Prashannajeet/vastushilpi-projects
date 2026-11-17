from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AppContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for name in ("index.html", "manifest.webmanifest", "sw.js", "icon.svg"):
            self.assertTrue((ROOT / name).is_file(), name)

    def test_core_field_workflow_is_present(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for marker in (
            "navigator.geolocation",
            'capture="environment"',
            "localStorage",
            "FeatureCollection",
            "Stormwater Drainage",
            "Road",
            "World_Imagery",
            "basemapSelect",
            "surveyMap",
            "watchPosition",
            "readonly required",
            "NITA GeoAI",
            "photoInput1",
            "photoInput2",
            "photoInput3",
            "compressedSize",
            "mobile-guide",
            "form-actions",
            "deviceTimestamp",
            "deviceTimezone",
            "MANDIDEEP_LAYER_CONFIG",
            "mandideep_osm_waterways_wgs84.geojson",
            'const RECORDS_API = "/api/field-survey/roads-drainage/records";',
            'const MAX_PHOTO_UPLOAD_BYTES = 180 * 1024;',
            'const MAX_SUBMISSION_BYTES = 900 * 1024;',
            'setInterval(bootstrapOnlineSync, 60000);',
            'syncStatus:"pending"',
        ):
            self.assertIn(marker, html)

    def test_mobile_sync_worker_is_versioned(self) -> None:
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertIn("nita-geoai-roads-drainage-online-v4", worker)

    def test_reference_layers_required_by_worker_are_published(self) -> None:
        for name in (
            "mandideep_aoi_wgs84.geojson",
            "mandideep_osm_roads_buffer100m_wgs84.geojson",
            "mandideep_osm_waterways_wgs84.geojson",
            "mandideep_osm_waterbodies_wgs84.geojson",
            "mandideep_osm_railways_wgs84.geojson",
            "mandideep_osm_flyovers_3d_wgs84.geojson",
        ):
            self.assertTrue((ROOT / "data" / name).is_file(), name)

    def test_no_old_project_or_cloud_credentials(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Mohanpura", html)
        self.assertNotIn("Kundaliya", html)
        self.assertNotIn("sb_publishable_", html)


if __name__ == "__main__":
    unittest.main()

