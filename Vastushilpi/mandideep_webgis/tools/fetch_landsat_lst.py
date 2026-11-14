"""Fetch and prepare a QA-masked Landsat Collection 2 LST layer for Mandideep.

The workflow searches Microsoft Planetary Computer's public STAC metadata,
signs the public Azure Blob assets, applies the USGS Collection 2 surface-
temperature scale factor, masks cloud/shadow/snow/fill pixels from QA_PIXEL,
and writes a compact web display raster plus an analysis GeoTIFF and manifest.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

for _site_path in sys.path:
    _rasterio_proj_data = Path(_site_path) / "rasterio" / "proj_data"
    if _rasterio_proj_data.exists():
        os.environ["PROJ_LIB"] = str(_rasterio_proj_data)
        break

import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.mask import mask
from rasterio.transform import from_bounds
from rasterio.warp import reproject
from shapely.geometry import shape


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data"
STAC_SEARCH = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
STAC_SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="
AOI_BOUNDS = (77.5030283, 23.0624953, 77.5799250, 23.1164963)
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 800
DISPLAY_MIN_C = 10.0
DISPLAY_MAX_C = 50.0
ST_SCALE = 0.00341802
ST_OFFSET_K = 149.0
QA_MASK_BITS = sum(1 << bit for bit in (0, 1, 2, 3, 4, 5))


def read_json(path: Path) -> dict:
    """Read a UTF-8 JSON document."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fetch_json(url: str, payload: dict | None = None) -> dict:
    """Fetch JSON from a public HTTP endpoint."""
    headers = {"Accept": "application/json"}
    request = urllib.request.Request(url, headers=headers, method="GET")
    if payload is not None:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def sign_asset(href: str) -> str:
    """Return a short-lived read URL for a Planetary Computer asset."""
    encoded = urllib.parse.quote(href, safe="")
    return fetch_json(STAC_SIGN + encoded)["href"]


def choose_item() -> dict:
    """Select the newest low-cloud Landsat C2 L2 scene intersecting Mandideep."""
    now = datetime.now(UTC)
    search = {
        "collections": ["landsat-c2-l2"],
        "bbox": list(AOI_BOUNDS),
        "datetime": f"2022-01-01T00:00:00Z/{now.isoformat().replace('+00:00', 'Z')}",
        "limit": 100,
        "query": {"eo:cloud_cover": {"lt": 20}},
    }
    items = fetch_json(STAC_SEARCH, search)["features"]
    if not items:
        raise RuntimeError("No Landsat C2 L2 scene with less than 20% cloud cover was found.")
    items.sort(key=lambda item: item["properties"]["datetime"], reverse=True)
    return items[0]


def apply_temperature_scale(dn: np.ndarray, qa: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Convert ST_B10 DN to Celsius and return a valid-pixel mask."""
    valid = (dn > 0) & ((qa & QA_MASK_BITS) == 0)
    celsius = (dn.astype(np.float32) * ST_SCALE + ST_OFFSET_K) - 273.15
    celsius[~valid] = np.nan
    return celsius, valid


def colourize(values: np.ndarray) -> np.ndarray:
    """Render Celsius values to a fixed 10–50 °C blue-to-red ramp."""
    stops = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    colours = np.array([[49, 54, 149], [69, 117, 180], [254, 224, 144], [244, 109, 67], [165, 0, 38]], dtype=float)
    clipped = np.clip(values, stops[0], stops[-1])
    rgb = np.stack([np.interp(clipped, stops, colours[:, band]) for band in range(3)], axis=-1)
    return rgb.astype(np.uint8)


def process_item(item: dict) -> dict:
    """Create the analysis GeoTIFF, web PNG, and provenance manifest."""
    aoi = read_json(DATA_DIR / "mandideep_aoi_wgs84.geojson")
    aoi_geometries = [feature["geometry"] for feature in aoi["features"]]
    lst_url = sign_asset(item["assets"]["lwir11"]["href"])
    qa_url = sign_asset(item["assets"]["qa_pixel"]["href"])

    with rasterio.open(lst_url) as lst_src, rasterio.open(qa_url) as qa_src:
        aoi_projected = [rasterio.warp.transform_geom("EPSG:4326", lst_src.crs, geometry) for geometry in aoi_geometries]
        lst_data, transform = mask(lst_src, aoi_projected, crop=True, nodata=0)
        qa_data, _ = mask(qa_src, aoi_projected, crop=True, nodata=0)
        celsius, valid = apply_temperature_scale(lst_data[0], qa_data[0])
        inside_aoi = geometry_mask(aoi_projected, out_shape=celsius.shape, transform=transform, invert=True)
        valid_inside = valid & inside_aoi
        valid_values = celsius[valid_inside]
        if valid_values.size == 0:
            raise RuntimeError("The selected Landsat scene has no valid QA-masked LST pixels inside the AOI.")

        analysis_path = DATA_DIR / "mandideep_landsat_lst_celsius_utm43n.tif"
        profile = lst_src.profile.copy()
        profile.update(
            driver="GTiff",
            dtype="float32",
            count=1,
            height=celsius.shape[0],
            width=celsius.shape[1],
            transform=transform,
            crs=lst_src.crs,
            nodata=-9999.0,
            compress="deflate",
            predictor=3,
            tiled=True,
            blockxsize=256,
            blockysize=256,
        )
        with rasterio.open(analysis_path, "w", **profile) as dst:
            dst.write(np.nan_to_num(celsius, nan=-9999.0).astype(np.float32), 1)

    west, south, east, north = AOI_BOUNDS
    dst_transform = from_bounds(west, south, east, north, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    display = np.full((DISPLAY_HEIGHT, DISPLAY_WIDTH), -9999.0, dtype=np.float32)
    with rasterio.open(analysis_path) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=display,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs="EPSG:4326",
            src_nodata=-9999.0,
            dst_nodata=-9999.0,
            resampling=Resampling.bilinear,
        )
    valid_display = display > -9990
    rgba = np.zeros((DISPLAY_HEIGHT, DISPLAY_WIDTH, 4), dtype=np.uint8)
    rgba[..., :3] = colourize(np.where(valid_display, display, DISPLAY_MIN_C))
    rgba[..., 3] = np.where(valid_display, 185, 0).astype(np.uint8)
    Image.fromarray(rgba, mode="RGBA").save(DATA_DIR / "mandideep_landsat_lst_celsius.png", optimize=True)

    properties = item["properties"]
    manifest = {
        "product": "Landsat Collection 2 Level-2 Surface Temperature",
        "platform": properties.get("platform"),
        "item_id": item["id"],
        "acquisition_datetime": properties.get("datetime"),
        "cloud_cover_percent": properties.get("eo:cloud_cover"),
        "source_stac": f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/{item['id']}",
        "source_provider": "USGS Landsat Collection 2 via Microsoft Planetary Computer STAC",
        "analysis_crs": "EPSG:32643",
        "display_crs": "EPSG:4326",
        "scale_factor": ST_SCALE,
        "additive_offset_kelvin": ST_OFFSET_K,
        "qa_pixel_mask_bits": {"fill": 0, "dilated_cloud": 1, "cirrus": 2, "cloud": 3, "cloud_shadow": 4, "snow": 5},
        "valid_pixel_percent": round(float(valid_inside.sum() / inside_aoi.sum() * 100), 2),
        "temperature_min_c": round(float(np.nanmin(valid_values)), 2),
        "temperature_max_c": round(float(np.nanmax(valid_values)), 2),
        "temperature_p02_c": round(float(np.nanpercentile(valid_values, 2)), 2),
        "temperature_p98_c": round(float(np.nanpercentile(valid_values, 98)), 2),
        "display_range_c": [DISPLAY_MIN_C, DISPLAY_MAX_C],
        "limitations": [
            "LST is radiative land-surface skin temperature, not near-surface air temperature.",
            "The displayed raster is resampled for web display; the analysis GeoTIFF remains the clipped 30 m product.",
            "Cloud, shadow, snow, and fill pixels are masked using QA_PIXEL bits 0–5.",
        ],
    }
    with (DATA_DIR / "mandideep_landsat_lst_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    LOGGER.info("Prepared %s from %s", analysis_path.name, item["id"])
    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    selected_item = choose_item()
    process_item(selected_item)
